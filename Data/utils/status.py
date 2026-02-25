import requests
def update_user_status(user):
    api_url = f"https://hr.example.com/status_check/{user.id}"
    try:
        response = requests.get(api_url, timeout=5)
        user.is_active = response.status_code == 200
    except requests.RequestException:
        # Fail-safe: don't deactivate user on temporary network failure
        pass
    else:
        user.save()