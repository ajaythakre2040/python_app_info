from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import app_data, domain_logs
from ..serializer import AppDataSerializer
from ..permissions.authentication import LoginTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..utils.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import app_data, domain_logs
from ..serializer import AppDataSerializer
from ..permissions.authentication import LoginTokenAuthentication
from ..utils.pagination import CustomPagination

class AppDataAPIView(APIView):

    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    # ========================================= GET =========================================
    def get(self, request, id=None):
        try:

            # ================= GET BY APP ID (Single Record) =================
            if id:
                instance = get_object_or_404(
                    app_data,
                    id=id,
                    deleted_at__isnull=True
                )

                data = AppDataSerializer(instance).data

                last_log = (
                    domain_logs.objects
                    .filter(app_data=instance)
                    .order_by('-created_at')
                    .first()
                )

                data["last_log"] = {
                    "url": last_log.url,
                    "status": last_log.status,
                    "created_at": last_log.created_at
                } if last_log else None

                return Response(
                    {"success": True, "data": data},
                    status=status.HTTP_200_OK
                )

            # ================= GET ALL (Latest 5 Overall Records) =================
            records = (
                app_data.objects
                .filter(deleted_at__isnull=True)
                .order_by('-created_at')[:5]
            )

            result = []

            for obj in records:
                data = AppDataSerializer(obj).data

                last_log = (
                    domain_logs.objects
                    .filter(app_data=obj)
                    .order_by('-created_at')
                    .first()
                )

                data["last_log"] = {
                    "url": last_log.url,
                    "status": last_log.status,
                    "created_at": last_log.created_at
                } if last_log else None

                result.append(data)

            return Response(
                {"success": True, "data": result},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========================================= POST =========================================
    def post(self, request):
        try:
            serializer = AppDataSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(
                    user=request.user,
                    created_by=request.user
                )
                return Response(
                    {"success": True, "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========================================= PATCH (Update by App ID) =========================================
    def patch(self, request, id=None):
        try:
            instance = get_object_or_404(
                app_data,
                id=id,
                deleted_at__isnull=True
            )

            serializer = AppDataSerializer(
                instance,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(
                    {"success": True, "data": serializer.data},
                    status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========================================= DELETE (Soft Delete) =========================================
    def delete(self, request, id=None):
        try:
            instance = get_object_or_404(
                app_data,
                id=id,
                deleted_at__isnull=True
            )

            instance.deleted_at = timezone.now()
            instance.deleted_by = request.user
            instance.save()

            return Response(
                {"success": True, "message": "Deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )