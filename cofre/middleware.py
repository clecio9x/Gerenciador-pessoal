# em cofre/middleware.py

from django.shortcuts import redirect
from django.urls import reverse, resolve

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # A lógica agora roda ANTES de a view ser processada
        is_pending = request.session.get('2fa_pending_verification', False)

        if is_pending:
            allowed_urls = ['otp_verify', 'logout']
            current_url_name = resolve(request.path_info).url_name

            # Se a URL atual não está na lista de permissões, redireciona
            if current_url_name not in allowed_urls:
                return redirect('otp_verify')

        # Se não houver pendência ou se a URL for permitida, continua normalmente
        response = self.get_response(request)
        return response
