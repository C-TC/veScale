################################################################################
# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
################################################################################
# Modification Copyright 2023 ByteDance Ltd. and/or its affiliates.
################################################################################

from common_dtensor import (
    DTensorTestBase,
    with_comms,
    skip_unless_torch_gpu,
)
from torch.testing._internal.common_utils import run_tests

import torch
import torch.distributed._functional_collectives as funcol

from vescale import dtensor
from vescale import DeviceMesh, Replicate, Shard, Partial
from vescale.dtensor.random import manual_seed
from vescale.dtensor.api import distribute_tensor


class DTensorConstructorTest(DTensorTestBase):
    @property
    def world_size(self):
        return 4

    def _assert_equal(self, x: torch.Tensor, y: torch.Tensor):
        self.assertEqual(
            x,
            y,
            atol=None,
            rtol=None,
            equal_nan=True,
            exact_dtype=True,
            exact_device=True,
            exact_layout=True,
            exact_stride=False,
            exact_is_coalesced=False,
        )
        self.assertTrue(x.requires_grad == y.requires_grad)

    def _assert_eq_empty(self, x: torch.Tensor, y: torch.Tensor):
        self.assertTrue(x.shape == y.shape)
        self.assertTrue(x.dtype == y.dtype)
        self.assertTrue(x.device.type == y.device.type)
        self.assertTrue(x.layout == y.layout)
        self.assertTrue(x.requires_grad == y.requires_grad)

    def _run_init_op(self, init_op, dist_init_op, eq_op, *args, **kwargs):
        # 1d mesh
        device_mesh = DeviceMesh(self.device_type, list(range(self.world_size)))
        placements_list = [[Shard(0)], [Shard(1)], [Shard(2)], [Replicate()], [Partial()]]

        # even sharding
        global_shape = [4, 8, 12]  # global shape
        for placements in placements_list:
            local_shape = global_shape.copy()
            if isinstance(placements[0], Shard):
                shard_dim = placements[0].dim
                local_shape[shard_dim] //= self.world_size

            dist_tensor = dist_init_op(
                global_shape,
                *args,
                **kwargs,
                device_mesh=device_mesh,
                placements=placements,
            )

            expected_tensor = init_op(local_shape, *args, **kwargs, device=self.device_type)
            if placements[0].is_partial() and self.rank != 0:
                with torch.no_grad():
                    expected_tensor.zero_()

            eq_op(dist_tensor.to_local(), expected_tensor)

        # uneven sharding
        global_shape = [5, 10, 15]
        for placements in placements_list:
            dist_tensor = dist_init_op(
                global_shape,
                *args,
                **kwargs,
                device_mesh=device_mesh,
                placements=placements,
            )
            if isinstance(placements[0], Shard):
                shard_dim = placements[0].dim
                expected_tensor_list = list(
                    torch.chunk(
                        init_op(global_shape, *args, **kwargs, device=self.device_type),
                        self.world_size,
                        dim=shard_dim,
                    )
                )
                if self.rank < len(expected_tensor_list):
                    eq_op(dist_tensor.to_local(), expected_tensor_list[self.rank])
            else:
                expected_tensor = init_op(global_shape, *args, **kwargs, device=self.device_type)
                if placements[0].is_partial() and self.rank != 0:
                    with torch.no_grad():
                        expected_tensor.zero_()

                eq_op(dist_tensor.to_local(), expected_tensor)

    @with_comms
    def test_zeros(self):
        self._run_init_op(
            torch.zeros,
            dtensor.zeros,
            self._assert_equal,
            requires_grad=True,
        )

    @with_comms
    def test_ones(self):
        self._run_init_op(
            torch.ones,
            dtensor.ones,
            self._assert_equal,
            requires_grad=True,
        )

    @with_comms
    def test_empty(self):
        self._run_init_op(
            torch.empty,
            dtensor.empty,
            self._assert_eq_empty,
            requires_grad=True,
        )

    @with_comms
    def test_full(self):
        self._run_init_op(
            torch.full,
            dtensor.full,
            self._assert_equal,
            123.4,
            requires_grad=True,
        )

    @with_comms
    @skip_unless_torch_gpu
    def test_randn(self):
        self._run_init_op(
            torch.randn,
            dtensor.randn,
            self._assert_eq_empty,
            requires_grad=True,
        )

    def _rand_init_self_compare(self, dist_init_op, *args, **kwargs):
        # 1d mesh
        device_mesh = DeviceMesh(self.device_type, list(range(self.world_size)))
        global_shape = (8, 4)

        # create DTensor
        manual_seed(0, device_mesh)
        dtensor = dist_init_op(
            global_shape,
            *args,
            **kwargs,
            device_mesh=device_mesh,
            placements=[Shard(1)],
        )
        local_tensor = dtensor.to_local()

        # allgather the local tensors
        dtensor = dtensor.redistribute(device_mesh, [Replicate()])
        global_tensor = dtensor.to_local()
        self.assertEqual(global_tensor.shape, global_shape)

        # compare global tensors from other ranks
        concat_global_tensor = funcol.all_gather_tensor(
            global_tensor, gather_dim=0, group=device_mesh._dim_group_infos[0][1]
        )
        for other_rank in range(self.world_size):
            if self.rank != other_rank:
                slice_idx = [
                    slice(other_rank * global_shape[0], (other_rank + 1) * global_shape[0]),
                    slice(global_shape[1]),
                ]
                # other rank should have a same global tensor
                print(f"randn value is {concat_global_tensor[slice_idx]} , and global is{global_tensor}")
                self.assertEqual(concat_global_tensor[slice_idx], global_tensor)

        # compare with local tensors from other ranks
        for other_rank in range(self.world_size):
            if self.rank != other_rank:
                slice_idx = [
                    slice(global_shape[0]),
                    slice(other_rank * global_shape[1], (other_rank + 1) * global_shape[1]),
                ]
                # other rank should have a different local tensor
                self.assertNotEqual(global_tensor[slice_idx], local_tensor)

    def _rand_init_compare(self, init_op, dist_init_op, *args, **kwargs):
        # 1d mesh
        device_mesh = DeviceMesh(self.device_type, list(range(self.world_size)))
        global_shape = (8, 4)

        # create golden Tensor
        torch.manual_seed(0)
        torch.cuda.manual_seed(0)
        expected_tensor = init_op(*global_shape, *args, **kwargs, device=self.device_type)

        # create DTensor
        manual_seed(0, device_mesh)
        dtensor = dist_init_op(
            global_shape,
            *args,
            **kwargs,
            device_mesh=device_mesh,
            placements=[Shard(1)],
        )

        # allgather the local tensors
        dtensor = dtensor.redistribute(device_mesh, [Replicate()])
        global_tensor = dtensor.to_local()
        self.assertEqual(global_tensor.shape, global_shape)

        # match
        self.assertEqual(global_tensor, expected_tensor)

    @skip_unless_torch_gpu
    @with_comms
    def test_randn_value(self):
        device_mesh = DeviceMesh(self.device_type, torch.arange(self.world_size))
        torch_op = torch.randn
        dtensor_op = dtensor.randn
        for global_shape in [
            (8,),
            (8, 9),
            (9, 10, 11, 12),
            (33, 11, 13),
        ]:
            all_placements = [[Replicate()], [Partial()]] + [[Shard(d)] for d in range(len(global_shape))]
            for placements in all_placements:
                torch.manual_seed(0)
                torch.cuda.manual_seed(0)
                expected_tensor = torch_op(global_shape, device=self.device_type)
                dist_expected = distribute_tensor(expected_tensor, device_mesh, placements)

                # create DTensor
                manual_seed(0, device_mesh)
                ve_tensor = dtensor_op(global_shape, device_mesh=device_mesh, placements=placements)

                self.assertEqual(ve_tensor.to_local(), dist_expected.to_local(), atol=0.0, rtol=0.0)
                global_tensor = ve_tensor.full_tensor()
                expected_tensor = dist_expected.full_tensor()
                self.assertEqual(global_tensor, expected_tensor, atol=0.0, rtol=0.0)

    @with_comms
    def test_arange(self):
        device_mesh = DeviceMesh(self.device_type, torch.arange(self.world_size))
        for start_end_step in [
            (4,),
            (5,),
            (0, 4),
            (0, 5),
            (0, 4, 1),
            (0, 5, 1),
            (11, 22, 2),
            (0, -10, -1),
            (2, -100, -3),
        ]:
            for placements in [[Replicate()], [Shard(0)], [Partial()]]:
                single = torch.arange(*start_end_step, device=self.device_type)
                golden = distribute_tensor(torch.arange(*start_end_step), device_mesh, placements)
                actual = dtensor.arange(*start_end_step, device_mesh=device_mesh, placements=placements)
                self.assertTrue(dtensor.equal(actual, golden), msg=f"mismatch: {start_end_step}, {placements}")
                self.assertTrue(
                    torch.equal(single, golden.redistribute(placements=[Replicate()])._local_tensor),
                    msg=f"mismatch: {start_end_step}, {placements}",
                )
                self.assertTrue(
                    torch.equal(single, actual.redistribute(placements=[Replicate()])._local_tensor),
                    msg=f"mismatch: {start_end_step}, {placements}",
                )

    @with_comms
    def test_zeros_full_mesh(self):
        # construct a device 1d mesh
        mesh = DeviceMesh(self.device_type, torch.arange(self.world_size))
        placements = [Shard(0)]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()
        self.assertEqual(local_tensor.size(), torch.Size([8, 3]))

        local_tensor = torch.zeros(8, 3)
        self.assertEqual(dist_tensor.to_local(), local_tensor)

        self.assertEqual(dist_tensor.device.type, self.device_type)

        # 1d sharded unevenly
        size = [31, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()
        if self.rank <= 2:
            self.assertEqual(local_tensor.size(), torch.Size([8, 3]))
            self.assertEqual(torch.zeros(8, 3), local_tensor)
        else:
            self.assertEqual(local_tensor.size(), torch.Size([7, 3]))
            self.assertEqual(torch.zeros(7, 3), local_tensor)

        # construct a device mesh with 2d: shard, replicate
        mesh = DeviceMesh(self.device_type, torch.arange(self.world_size).reshape(2, 2))
        placements = [Shard(0), Replicate()]
        size = [32, 4]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)

        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()
        self.assertEqual(local_tensor.size(), torch.Size([16, 4]))
        self.assertEqual(local_tensor, torch.zeros([16, 4]))

        # construct a device mesh with 2d: shard, shard
        placements = [Shard(0), Shard(1)]
        size = [32, 4]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)

        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()
        self.assertEqual(local_tensor.size(), torch.Size([16, 2]))
        self.assertEqual(local_tensor, torch.zeros([16, 2]))

        # 2d sharded unevenly
        placements = [Shard(0), Shard(1)]
        size = [31, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)

        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()
        if self.rank == 0:
            self.assertEqual(local_tensor, torch.zeros([16, 2]))
        elif self.rank == 1:
            self.assertEqual(local_tensor, torch.zeros([16, 1]))
        elif self.rank == 2:
            self.assertEqual(local_tensor, torch.zeros([15, 2]))
        elif self.rank == 3:
            self.assertEqual(local_tensor, torch.zeros([15, 1]))

    @with_comms
    def test_zeros_submesh(self):
        # default world_size is 4
        # construct a device 1d mesh, with no sub pg initialized
        sub_mesh_list = [0, 3]
        mesh = DeviceMesh(self.device_type, sub_mesh_list, _init_process_groups=False)
        placements = [Shard(0)]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()

        if self.rank in sub_mesh_list:
            self.assertEqual(local_tensor.size(), torch.Size([16, 3]))
            self.assertEqual(local_tensor, torch.zeros([16, 3]))
        else:
            self.assertEqual(local_tensor.size(), torch.Size([0]))
            self.assertEqual(local_tensor, torch.tensor([]))

        # construct a device 1d mesh, with no sub pg initialized
        sub_mesh_list = [0, 3]
        mesh = DeviceMesh(self.device_type, sub_mesh_list, _init_process_groups=False)
        placements = [Partial()]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()

        if self.rank in sub_mesh_list:
            self.assertEqual(local_tensor.size(), torch.Size([32, 3]))
            self.assertEqual(local_tensor, torch.zeros([32, 3]))
        else:
            self.assertEqual(local_tensor.size(), torch.Size([0]))
            self.assertEqual(local_tensor, torch.tensor([]))

        # construct a device 1d mesh: unevenly, with subpg initialized
        sub_mesh_list = [0, 1, 3]
        mesh = DeviceMesh(self.device_type, sub_mesh_list)
        placements = [Shard(0)]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()

        if self.rank in sub_mesh_list:
            if self.rank != 3:
                self.assertEqual(local_tensor.size(), torch.Size([11, 3]))
                self.assertEqual(local_tensor, torch.zeros([11, 3]))
            else:
                self.assertEqual(local_tensor.size(), torch.Size([10, 3]))
                self.assertEqual(local_tensor, torch.zeros([10, 3]))
        else:
            self.assertEqual(local_tensor.size(), torch.Size([0]))
            self.assertEqual(local_tensor, torch.tensor([]))

        # construct a device 2d mesh, with no subpg initialized
        sub_mesh_list = [[0], [3]]
        mesh = DeviceMesh(self.device_type, sub_mesh_list, _init_process_groups=False)
        placements = [Shard(0), Shard(1)]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()

        if self.rank in [0, 3]:
            self.assertEqual(local_tensor.size(), torch.Size([16, 3]))
            self.assertEqual(local_tensor, torch.zeros([16, 3]))
        else:
            self.assertEqual(local_tensor.size(), torch.Size([0]))
            self.assertEqual(local_tensor, torch.tensor([]))

        # construct a device 2d mesh, with no subpg initialized
        sub_mesh_list = [[0], [3]]
        mesh = DeviceMesh(self.device_type, sub_mesh_list, _init_process_groups=False)
        placements = [Shard(0), Partial()]
        size = [32, 3]
        dist_tensor = dtensor.zeros(size, device_mesh=mesh, placements=placements)
        self.assertEqual(dist_tensor.size(), torch.Size(size))
        local_tensor = dist_tensor.to_local()

        if self.rank in [0, 3]:
            self.assertEqual(local_tensor.size(), torch.Size([16, 3]))
            self.assertEqual(local_tensor, torch.zeros([16, 3]))
        else:
            self.assertEqual(local_tensor.size(), torch.Size([0]))
            self.assertEqual(local_tensor, torch.tensor([]))

    @with_comms
    def test_partial_2D_mesh(self):
        """
        DT         = [1, 1, 1, 1]
                     [1, 1, 1, 1]
                     [1, 1, 1, 1]
                     [1, 1, 1, 1]

        DeviceMesh = [0 1]
                     [2 3]
        """
        global_shape = (4, 4)
        device_mesh = DeviceMesh(self.device_type, torch.arange(self.world_size).reshape(2, 2))

        def _assert_case(placements, local_shape, true_ranks):
            dt = dtensor.ones(global_shape, device_mesh=device_mesh, placements=placements)
            if self.rank in true_ranks:
                expected_tensor = torch.ones(local_shape, device=self.device_type)
            else:
                expected_tensor = torch.zeros(local_shape, device=self.device_type)
            self.assertEqual(dt.to_local(), expected_tensor)

        _assert_case([Shard(0), Partial()], (2, 4), (0, 2))
        _assert_case([Shard(1), Partial()], (4, 2), (0, 2))
        _assert_case([Replicate(), Partial()], (4, 4), (0, 2))
        _assert_case([Partial(), Shard(0)], (2, 4), (0, 1))
        _assert_case([Partial(), Shard(1)], (4, 2), (0, 1))
        _assert_case([Partial(), Replicate()], (4, 4), (0, 1))
        _assert_case([Partial(), Partial()], (4, 4), (0,))


if __name__ == "__main__":
    run_tests()
