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


    # ========================================= GET =========================================
    def get(self, request, id=None):
        try:

            # ================= GET BY ID =================
            if id:

                domain_obj = app_data.objects.filter(
                    id=id,
                    deleted_at__isnull=True
                ).first()

                if not domain_obj:
                    return Response(
                        {"success": False, "message": "Domain not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                logs_queryset = domain_logs.objects.filter(
                    app_data=domain_obj
                ).order_by("-created_at")

                domain_info = AppDataSerializer(domain_obj).data

                logs = []

                for log in logs_queryset:
                    logs.append({
                        "id": log.id,
                        "url": log.url,
                        "status": log.status,
                        "json_result": log.json_result,
                        "created_at": log.created_at
                    })

                return Response(
                    {
                        "success": True,
                        "domain_details": domain_info,
                        "history_logs": logs
                    },
                    status=status.HTTP_200_OK
                )


            # ================= GET ALL =================
            queryset = app_data.objects.filter(
                deleted_at__isnull=True
            ).order_by("user", "-created_at")

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)

            result = []

            for obj in page:

                data = AppDataSerializer(obj).data

                latest_log = (
                    domain_logs.objects
                    .filter(app_data=obj)
                    .order_by("-created_at")
                    .first()
                )

                data["latest_status"] = (
                    {
                        "status": latest_log.status,
                        "http_status": (
                            latest_log.json_result.get("http_status")
                            if latest_log and latest_log.json_result
                            else None
                        ),
                        "last_checked": latest_log.created_at
                    }
                    if latest_log else None
                )

                result.append(data)

            return paginator.get_paginated_response({
                "success": True,
                "all_domains": result
            })


        except Exception as e:

            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    # ========================================= POST =========================================
    def post(self, request):

        serializer = AppDataSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(
                user=request.user,
                created_by=request.user
            )

            return Response(
                {
                    "success": True,
                    "message": "Domain created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # ========================================= PATCH =========================================
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
                    {
                        "success": True,
                        "message": "Updated successfully",
                        "data": serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    # ========================================= DELETE =========================================
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
                {
                    "success": True,
                    "message": "Deleted successfully"
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )