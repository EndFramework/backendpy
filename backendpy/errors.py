from .response.formatted import ErrorList, ErrorCode
from .response.response import Status

errors = ErrorList(
    ErrorCode(1000, "Server error: {}", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1001, "Request data receive error: {}", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1002, "Middleware error: {}", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1003, "Handler error: {}", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1004, "Data handler error: {}", Status.INTERNAL_SERVER_ERROR),
    ErrorCode(1005, "Not found", Status.NOT_FOUND),
    ErrorCode(1006, "Unexpected data", Status.BAD_REQUEST),
)
