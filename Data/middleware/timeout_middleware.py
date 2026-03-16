import threading
from django.http import JsonResponse

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        result = {}

        def target():
            try:
                result['response'] = self.get_response(request)
            except Exception as e:
                result['response'] = JsonResponse(
                    {"success": False, "message": str(e)}, status=500
                )

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=30)  # 30 sec timeout

        if thread.is_alive():
            return JsonResponse(
                {"success": False, "message": "Request timed out. Please try again."},
                status=408
            )

        return result.get('response')