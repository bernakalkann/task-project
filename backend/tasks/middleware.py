import time
from .models import RequestLog

class RequestLogMiddleware:
    """
    Sistemdeki bütün HTTP isteklerini loglayan middleware.
    IP, Kullanıcı, User-Agent, Method, Endpoint, Status Code, vb. bilgileri tutar.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Sadece /api/ endpoint'lerini logla veya tüm istekleri logla
        # Static files veya admin assets haricindeki istekler loglansın
        path = request.path
        if not path.startswith('/static/') and not path.startswith('/media/'):
            try:
                ip = self.get_client_ip(request)
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                username = user.username if user else 'Anonymous'
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                RequestLog.objects.create(
                    user=user,
                    username=username,
                    ip_address=ip,
                    user_agent=user_agent,
                    method=request.method,
                    endpoint=path,
                    status_code=response.status_code
                )
            except Exception as e:
                # Loglama hatası ana akışı bozmamalı
                pass

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
