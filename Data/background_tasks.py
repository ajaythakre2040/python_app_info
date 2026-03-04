import threading
import time
import requests
from django.utils import timezone
from django.db import connections

# Absolute Imports (Apne model paths ke hisab se)
from data.models.data_app import app_data
from data.models.logs_domain import domain_logs


def start_monitoring():
    while True:
        try:
            # Saare domains uthayein jo delete nahi hue hain
            domains = app_data.objects.filter(deleted_at__isnull=True)

            for domain in domains:
                # 1. Domain Status Check
                try:
                    response = requests.get(domain.url, timeout=10)
                    is_active = response.status_code == 200
                    http_status = response.status_code
                except Exception:
                    is_active = False
                    http_status = None

                # 2. Update Main Table (Only if status changed)
                if domain.status != is_active:
                    domain.status = is_active
                    domain.save(update_fields=["status"])

                # 3. Create NEW Log
                domain_logs.objects.create(
                    app_data=domain,
                    url=domain.url,
                    status=is_active,
                    json_result={
                        "http_status": http_status,
                        "checked_at": str(timezone.now()),
                    },
                )

                # 4. Keep ONLY 5 Logs (Old delete logic)
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
            print(f"Error in monitoring loop: {e}")

        # 5. Database connection clean karein aur 2 min wait karein
        connections.close_all()
        time.sleep(60)


def run_background_monitor():
    # Thread start karein
    thread = threading.Thread(target=start_monitoring, daemon=True)
    thread.start()
