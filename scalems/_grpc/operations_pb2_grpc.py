# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.longrunning import operations_pb2 as google_dot_longrunning_dot_operations__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class OperationsStub(object):
  """Manages long-running operations with an API service.

  When an API method normally takes long time to complete, it can be designed
  to return [Operation][google.longrunning.Operation] to the client, and the client can use this
  interface to receive the real response asynchronously by polling the
  operation resource, or pass the operation resource to another API (such as
  Google Cloud Pub/Sub API) to receive the response.  Any API service that
  returns long-running operations should implement the `Operations` interface
  so developers can have a consistent client experience.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ListOperations = channel.unary_unary(
        '/google.longrunning.Operations/ListOperations',
        request_serializer=google_dot_longrunning_dot_operations__pb2.ListOperationsRequest.SerializeToString,
        response_deserializer=google_dot_longrunning_dot_operations__pb2.ListOperationsResponse.FromString,
        )
    self.GetOperation = channel.unary_unary(
        '/google.longrunning.Operations/GetOperation',
        request_serializer=google_dot_longrunning_dot_operations__pb2.GetOperationRequest.SerializeToString,
        response_deserializer=google_dot_longrunning_dot_operations__pb2.Operation.FromString,
        )
    self.DeleteOperation = channel.unary_unary(
        '/google.longrunning.Operations/DeleteOperation',
        request_serializer=google_dot_longrunning_dot_operations__pb2.DeleteOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.CancelOperation = channel.unary_unary(
        '/google.longrunning.Operations/CancelOperation',
        request_serializer=google_dot_longrunning_dot_operations__pb2.CancelOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.WaitOperation = channel.unary_unary(
        '/google.longrunning.Operations/WaitOperation',
        request_serializer=google_dot_longrunning_dot_operations__pb2.WaitOperationRequest.SerializeToString,
        response_deserializer=google_dot_longrunning_dot_operations__pb2.Operation.FromString,
        )


class OperationsServicer(object):
  """Manages long-running operations with an API service.

  When an API method normally takes long time to complete, it can be designed
  to return [Operation][google.longrunning.Operation] to the client, and the client can use this
  interface to receive the real response asynchronously by polling the
  operation resource, or pass the operation resource to another API (such as
  Google Cloud Pub/Sub API) to receive the response.  Any API service that
  returns long-running operations should implement the `Operations` interface
  so developers can have a consistent client experience.
  """

  def ListOperations(self, request, context):
    """Lists operations that match the specified filter in the request. If the
    server doesn't support this method, it returns `UNIMPLEMENTED`.

    NOTE: the `name` binding allows API services to override the binding
    to use different resource name schemes, such as `users/*/operations`. To
    override the binding, API services can add a binding such as
    `"/v1/{name=users/*}/operations"` to their service configuration.
    For backwards compatibility, the default name includes the operations
    collection id, however overriding users must ensure the name binding
    is the parent resource, without the operations collection id.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperation(self, request, context):
    """Gets the latest state of a long-running operation.  Clients can use this
    method to poll the operation result at intervals as recommended by the API
    service.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteOperation(self, request, context):
    """Deletes a long-running operation. This method indicates that the client is
    no longer interested in the operation result. It does not cancel the
    operation. If the server doesn't support this method, it returns
    `google.rpc.Code.UNIMPLEMENTED`.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CancelOperation(self, request, context):
    """Starts asynchronous cancellation on a long-running operation.  The server
    makes a best effort to cancel the operation, but success is not
    guaranteed.  If the server doesn't support this method, it returns
    `google.rpc.Code.UNIMPLEMENTED`.  Clients can use
    [Operations.GetOperation][google.longrunning.Operations.GetOperation] or
    other methods to check whether the cancellation succeeded or whether the
    operation completed despite cancellation. On successful cancellation,
    the operation is not deleted; instead, it becomes an operation with
    an [Operation.error][google.longrunning.Operation.error] value with a [google.rpc.Status.code][google.rpc.Status.code] of 1,
    corresponding to `Code.CANCELLED`.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def WaitOperation(self, request, context):
    """Waits for the specified long-running operation until it is done or reaches
    at most a specified timeout, returning the latest state.  If the operation
    is already done, the latest state is immediately returned.  If the timeout
    specified is greater than the default HTTP/RPC timeout, the HTTP/RPC
    timeout is used.  If the server does not support this method, it returns
    `google.rpc.Code.UNIMPLEMENTED`.
    Note that this method is on a best-effort basis.  It may return the latest
    state before the specified timeout (including immediately), meaning even an
    immediate response is no guarantee that the operation is done.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_OperationsServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ListOperations': grpc.unary_unary_rpc_method_handler(
          servicer.ListOperations,
          request_deserializer=google_dot_longrunning_dot_operations__pb2.ListOperationsRequest.FromString,
          response_serializer=google_dot_longrunning_dot_operations__pb2.ListOperationsResponse.SerializeToString,
      ),
      'GetOperation': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperation,
          request_deserializer=google_dot_longrunning_dot_operations__pb2.GetOperationRequest.FromString,
          response_serializer=google_dot_longrunning_dot_operations__pb2.Operation.SerializeToString,
      ),
      'DeleteOperation': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteOperation,
          request_deserializer=google_dot_longrunning_dot_operations__pb2.DeleteOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'CancelOperation': grpc.unary_unary_rpc_method_handler(
          servicer.CancelOperation,
          request_deserializer=google_dot_longrunning_dot_operations__pb2.CancelOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'WaitOperation': grpc.unary_unary_rpc_method_handler(
          servicer.WaitOperation,
          request_deserializer=google_dot_longrunning_dot_operations__pb2.WaitOperationRequest.FromString,
          response_serializer=google_dot_longrunning_dot_operations__pb2.Operation.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'google.longrunning.Operations', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
