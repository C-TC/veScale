################################################################################
#
# Copyright 2023 ByteDance Ltd. and/or its affiliates. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc

from . import (
    mem_file_service_pb2 as OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2,
)


class OmniStoreMemFileServiceStub:
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Write = channel.stream_unary(
            "/OmniStoreMemFileService/Write",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteResponse.FromString,
        )
        self.Read = channel.unary_stream(
            "/OmniStoreMemFileService/Read",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadResponse.FromString,
        )
        self.Rename = channel.unary_unary(
            "/OmniStoreMemFileService/Rename",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameResponse.FromString,
        )
        self.Remove = channel.unary_unary(
            "/OmniStoreMemFileService/Remove",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveResponse.FromString,
        )
        self.Listdir = channel.unary_unary(
            "/OmniStoreMemFileService/Listdir",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirResponse.FromString,
        )
        self.Exists = channel.unary_unary(
            "/OmniStoreMemFileService/Exists",
            request_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsRequest.SerializeToString,
            response_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsResponse.FromString,
        )


class OmniStoreMemFileServiceServicer:
    """Missing associated documentation comment in .proto file."""

    def Write(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Read(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Rename(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Remove(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Listdir(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Exists(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_OmniStoreMemFileServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Write": grpc.stream_unary_rpc_method_handler(
            servicer.Write,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteResponse.SerializeToString,
        ),
        "Read": grpc.unary_stream_rpc_method_handler(
            servicer.Read,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadResponse.SerializeToString,
        ),
        "Rename": grpc.unary_unary_rpc_method_handler(
            servicer.Rename,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameResponse.SerializeToString,
        ),
        "Remove": grpc.unary_unary_rpc_method_handler(
            servicer.Remove,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveResponse.SerializeToString,
        ),
        "Listdir": grpc.unary_unary_rpc_method_handler(
            servicer.Listdir,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirResponse.SerializeToString,
        ),
        "Exists": grpc.unary_unary_rpc_method_handler(
            servicer.Exists,
            request_deserializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsRequest.FromString,
            response_serializer=OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("OmniStoreMemFileService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class OmniStoreMemFileService:
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Write(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            "/OmniStoreMemFileService/Write",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreWriteResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Read(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/OmniStoreMemFileService/Read",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreReadResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Rename(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OmniStoreMemFileService/Rename",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRenameResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Remove(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OmniStoreMemFileService/Remove",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreRemoveResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Listdir(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OmniStoreMemFileService/Listdir",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreListdirResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Exists(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OmniStoreMemFileService/Exists",
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsRequest.SerializeToString,
            OmniStore_dot_utilities_dot_server_dot_mem__file__service__pb2.OmniStoreExistsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
