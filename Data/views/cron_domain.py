import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import app_data, domain_logs


# ========================= Helper Functions =========================
def check_domain_status(domain):

    try:
        response = requests.get(domain.url, timeout=10)
        is_active = response.status_code == 200
        debug_info = {
            "url": domain.url,
            "http_status": response.status_code,
            "exception": None
        }
        return is_active, debug_info
    except requests.RequestException as e:
        return False, {
            "url": domain.url,
            "http_status": None,
            "exception": str(e)
        }


def update_domain_status(domain):

    is_active, debug_info = check_domain_status(domain)

    # Update app_data status
    domain.status = is_active
    domain.save()

    # Check last log
    last_log = domain_logs.objects.filter(app_data=domain).order_by('-created_at').first()

    if not last_log or last_log.status != is_active:
        domain_logs.objects.create(
            app_data=domain,
            status=is_active,
            json_result={
                "status": 200 if is_active else 0,
                "active": is_active,
                "debug": debug_info
            }
        )

    return is_active, debug_info


# ========================= All Domains Cron =========================
class CronDomainStatusAPIView(APIView):
    def get(self, request):
        result = []

        domains = app_data.objects.filter(deleted_at__isnull=True)

        for domain in domains:
            is_active, debug_info = update_domain_status(domain)

            result.append({
                "title": domain.title,
                "url": domain.url,
                "checked_status": is_active,
                "debug": debug_info
            })

        return Response({
            "success": True,
            "checked_domains": result
        }, status=status.HTTP_200_OK)


# ========================= Active Domains Cron =========================
class ActiveDomainCronAPIView(APIView):
    def get(self, request):
        result = []

        domains = app_data.objects.filter(status=True, deleted_at__isnull=True)

        for domain in domains:
            is_active, debug_info = update_domain_status(domain)

            result.append({
                "title": domain.title,
                "url": domain.url,
                "checked_status": is_active,
                "debug": debug_info
            })

        return Response({
            "type": "Active Domains Checked",
            "success": True,
            "data": result
        }, status=status.HTTP_200_OK)


# ========================= Deactive Domains Cron =========================
class DeactiveDomainCronAPIView(APIView):
    def get(self, request):
        result = []

        domains = app_data.objects.filter(status=False, deleted_at__isnull=True)

        for domain in domains:
            is_active, debug_info = update_domain_status(domain)

            result.append({
                "title": domain.title,
                "url": domain.url,
                "checked_status": is_active,
                "debug": debug_info
            })

        return Response({
            "type": "Deactive Domains Checked",
            "success": True,
            "data": result
        }, status=status.HTTP_200_OK)