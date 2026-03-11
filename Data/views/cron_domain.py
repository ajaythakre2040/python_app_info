import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import app_data, domain_logs
from ..permissions.authentication import LoginTokenAuthentication
from rest_framework.permissions import IsAuthenticated

def check_domain_status(domain):
    try:
        response = requests.get(domain.url, timeout=10)
        is_active = response.status_code == 200
        debug_info = {
            "url": domain.url,
            "http_status": response.status_code,
            "exception": None,
        }
        return is_active, debug_info
    except requests.RequestException as e:
        return False, {
            "url": domain.url,
            "http_status": None,
            "exception": str(e),
        }


def update_domain_status(domain):
    is_active, debug_info = check_domain_status(domain)
    if domain.status != is_active:
        domain.status = is_active
        domain.save(update_fields=["status"])
    domain_logs.objects.create(
        app_data=domain,
        url=domain.url,
        status=is_active,
        json_result={
            "http_status": debug_info["http_status"],
            "active": is_active,
            "exception": debug_info["exception"],
        },
    )
    recent_logs_ids = (
        domain_logs.objects.filter(app_data=domain)
        .order_by("-created_at")
        .values_list("id", flat=True)[:5]
    )
    domain_logs.objects.filter(app_data=domain).exclude(id__in=recent_logs_ids).delete()
    return is_active, debug_info


class CronDomainStatusAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        result = []
        domains = app_data.objects.filter(deleted_at__isnull=True)
        for domain in domains:
            is_active, debug_info = update_domain_status(domain)
            result.append(
                {
                    "title": domain.title,
                    "url": domain.url,
                    "checked_status": is_active,
                    "debug": debug_info,
                }
            )
        return Response(
            {"success": True, "checked_domains": result}, status=status.HTTP_200_OK
        )


class ActiveDomainCronAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        result = []
        domains = app_data.objects.filter(status=True, deleted_at__isnull=True)
        for domain in domains:
            is_active, debug_info = update_domain_status(domain)
            result.append(
                {
                    "title": domain.title,
                    "url": domain.url,
                    "checked_status": is_active,
                    "debug": debug_info,
                }
            )
        return Response(
            {"type": "Active Domains Checked", "success": True, "data": result},
            status=status.HTTP_200_OK,
        )


class DeactiveDomainCronAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        result = []
        domains = app_data.objects.filter(status=False, deleted_at__isnull=True)
        for domain in domains:
            is_active, debug_info = update_domain_status(domain)
            result.append(
                {
                    "title": domain.title,
                    "url": domain.url,
                    "checked_status": is_active,
                    "debug": debug_info,
                }
            )
        return Response(
            {"type": "Deactive Domains Checked", "success": True, "data": result},
            status=status.HTTP_200_OK,
        )
