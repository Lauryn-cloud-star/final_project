from django.utils import timezone

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last activity timestamp
            request.user.last_activity = timezone.now()
            request.user.update_online_status()
            
        response = self.get_response(request)
        return response