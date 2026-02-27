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

class AppDataAPIView(APIView):

    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, id=None):
        try:

            # ================= GET BY USER ID (Latest 1 record) =================
            if id:
                instance = (
                    app_data.objects
                    .filter(
                        user_id=id,
                        deleted_at__isnull=True
                    )
                    .order_by('-created_at')
                    .first()
                )

                if not instance:
                    return Response(
                        {"message": "No data found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                data = AppDataSerializer(instance).data

                last_log = (
                    domain_logs.objects
                    .filter(app_data=instance)
                    .order_by('-created_at')
                    .first()
                )

                data["last_logs"] = [{
                    "url": last_log.url,
                    "status": last_log.status,
                    "created_at": last_log.created_at
                }] if last_log else []

                return Response(
                    {"success": True, "data": data},
                    status=status.HTTP_200_OK
                )

            # ================= GET ALL (Har User ke Latest 5 Records) =================

            user_ids = (
                app_data.objects
                .filter(deleted_at__isnull=True)
                .values_list('user_id', flat=True)
                .distinct()
            )

            result = []

            for user_id in user_ids:

                user_records = (
                    app_data.objects
                    .filter(
                        user_id=user_id,
                        deleted_at__isnull=True
                    )
                    .order_by('-created_at')[:5]
                )

                for obj in user_records:

                    data = AppDataSerializer(obj).data

                    logs = (
                        domain_logs.objects
                        .filter(app_data=obj)
                        .order_by('-created_at')[:5]
                    )

                    data["last_logs"] = [
                        {
                            "url": log.url,
                            "status": log.status,
                            "created_at": log.created_at
                        }
                        for log in logs
                    ]

                    result.append(data)

            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(result, request)

            return paginator.get_paginated_response({
                "success": True,
                "data": paginated_data
            })


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

    # ========================================= PUT =========================================
    def put(self, request, id=None):
        try:
            instance = get_object_or_404(
                app_data,
                id=id,
                user=request.user,
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
                user=request.user,
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