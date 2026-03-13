from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, DataError, ProgrammingError
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied


def custom_exception_handler(exc, context):
    """
    Global exception handler for DRF
    """

    response = exception_handler(exc, context)

    # DRF handled exceptions (Validation, Auth etc.)
    if response is not None:
        message = response.data

        if isinstance(exc, ValidationError):
            if isinstance(response.data, dict):
                message = "; ".join([f"{k}: {', '.join(v) if isinstance(v, list) else str(v)}" for k, v in response.data.items()])
            else:
                message = str(response.data)

        elif isinstance(exc, AuthenticationFailed):
            message = "Authentication failed."

        elif isinstance(exc, PermissionDenied):
            message = "You do not have permission to perform this action."

        return Response(
            {
                "success": False,
                "message": message
            },
            status=response.status_code
        )

    # Database duplicate error
    if isinstance(exc, IntegrityError):
        return Response(
            {
                "success": False,
                "message": "Duplicate entry found. Please use unique values."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Database value too long error
    if isinstance(exc, DataError):
        return Response(
            {
                "success": False,
                "message": "Input value exceeds the allowed length."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Other database errors
    if isinstance(exc, ProgrammingError):
        return Response(
            {
                "success": False,
                "message": "A database error occurred."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Fallback error
    return Response(
        {
            "success": False,
            "message": "An unexpected error occurred."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )