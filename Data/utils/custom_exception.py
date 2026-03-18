from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, DataError, ProgrammingError
from rest_framework.exceptions import (ValidationError,AuthenticationFailed,PermissionDenied,NotAuthenticated)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # ✅ DRF handled exceptions
    if response is not None:

        # 🔹 Validation Error (clean format)
        if isinstance(exc, ValidationError):
            if isinstance(response.data, dict):
                message = "; ".join([
                    f"{k}: {', '.join(v) if isinstance(v, list) else str(v)}"
                    for k, v in response.data.items()
                ])
            else:
                message = str(response.data)

        # 🔹 Auth + Permission (IMPORTANT: keep original message)
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated, PermissionDenied)):
            message = str(exc)

        # 🔹 Other DRF errors
        else:
            message = response.data.get("detail", str(response.data))

        return Response(
            {
                "success": False,
                "message": message
            },
            status=response.status_code
        )

    # ❌ Database Errors
    if isinstance(exc, IntegrityError):
        return Response(
            {
                "success": False,
                "message": "Duplicate entry found. Please use unique values."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, DataError):
        return Response(
            {
                "success": False,
                "message": "Input value exceeds allowed limit."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, ProgrammingError):
        return Response(
            {
                "success": False,
                "message": "Database error occurred."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # ❌ Fallback
    return Response(
        {
            "success": False,
            "message": "Something went wrong. Please try again later."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )