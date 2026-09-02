import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("mechanics")


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default handler to always return a consistent shape:
    { "error": true, "message": "...", "details": {...} }
    and logs unexpected (500-level) errors.
    """
    response = exception_handler(exc, context)

    if response is not None:
        details = response.data
        if isinstance(details, dict) and "detail" in details and len(details) == 1:
            message = str(details["detail"])
        else:
            message = "Validation failed."

        response.data = {
            "error": True,
            "message": message,
            "details": details,
        }
        return response

    logger.exception("Unhandled exception in %s", context.get("view"))
    return Response(
        {
            "error": True,
            "message": "Internal server error.",
            "details": str(exc),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )