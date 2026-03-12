from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, DataError, ProgrammingError

def custom_exception_handler(exc, context):
    """
    Global exception handler for DRF
    """
    # DRF built-in validation errors (serializer errors)
    response = exception_handler(exc, context)
    if response is not None:
        return Response({
            "success": False,
            "message": response.data
        }, status=response.status_code)

    # Database duplicate error
    if isinstance(exc, IntegrityError):
        return Response({
            "success": False,
            "message": "Duplicate entry found. Please use unique values."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Database value too long error
    if isinstance(exc, DataError):
        # don't expose raw database text; return a fixed, user‑friendly message
        return Response({
            "success": False,
            "message": "Input value exceeds the allowed length."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Catch-all for other database errors
    if isinstance(exc, ProgrammingError):
        return Response({
            "success": False,
            "message": "Database error occurred."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Other unhandled errors
    return Response({
        "success": False,
        "message": "Internal server error"
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)