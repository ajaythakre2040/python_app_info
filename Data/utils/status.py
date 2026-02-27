import requests
from time import sleep

def update_user_status(user, retries=3):
    api_url = f"https://hr.example.com/status_check/{user.id}"
    for attempt in range(retries):
        try:
            response = requests.get(api_url, timeout=5)
            user.status = response.status_code == 200
        except requests.RequestException:
            sleep(2) 
            continue
        else:
            user.save()
            break
