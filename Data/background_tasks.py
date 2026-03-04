import threading
import time
import requests
import urllib3
from django.utils import timezone
from django.db import connections

# SSL Warnings ko band karne ke liye (Kyunki hum verify=False use karenge)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Absolute Imports
from data.models.data_app import app_data
from data.models.logs_domain import domain_logs


def start_monitoring():
    while True:
        try:
            domains = app_data.objects.filter(deleted_at__isnull=True)

            for domain in domains:
                try:
                    # 1. Browser jaisa Header (Zaroori hai block hone se bachne ke liye)
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    }

                    # 2. Domain Status Check (with SSL Bypass & Headers)
                    # verify=False Berar Finance ke internal SSL issue ko solve karega
                    response = requests.get(
                        domain.url, timeout=20, headers=headers, verify=False
                    )

                    is_active = response.status_code == 200
                    http_status = response.status_code
                    error_msg = None

                except Exception as e:
                    is_active = False
                    http_status = None
                    error_msg = str(e)
                    print(f"Error checking {domain.url}: {error_msg}")

                # 3. Update Main Table (Only if status changed)
                if domain.status != is_active:
                    domain.status = is_active
                    domain.save(update_fields=["status"])

                # 4. Create NEW Log
                domain_logs.objects.create(
                    app_data=domain,
                    url=domain.url,
                    status=is_active,
                    json_result={
                        "http_status": http_status,
                        "checked_at": str(timezone.now()),
                        "error": error_msg,  # Debugging ke liye error save karein
                    },
                )

                # 5. Keep ONLY 5 Logs
                all_logs = domain_logs.objects.filter(app_data=domain).order_by(
                    "-created_at"
                )
                if all_logs.count() > 5:
                    ids_to_keep = list(all_logs.values_list("id", flat=True)[:5])
                    domain_logs.objects.filter(app_data=domain).exclude(
                        id__in=ids_to_keep
                    ).delete()

            print(f"[{timezone.now()}] Monitoring: All domains checked.")

        except Exception as e:
            print(f"Fatal error in monitoring loop: {e}")

        # Database connections saaf karein aur 2 min wait karein
        connections.close_all()
        time.sleep(120)  # 2 Minutes


def run_background_monitor():
    thread = threading.Thread(target=start_monitoring, daemon=True)
    thread.start()
