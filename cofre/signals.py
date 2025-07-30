# em cofre/signals.py

from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from django_otp import devices_for_user
from django_otp import login as otp_login

@receiver(user_logged_in)
def post_login_2fa_check(sender, request, user, **kwargs):
    """
    Esta função é executada toda vez que um usuário faz login.
    """
    # Verifica se o usuário tem um dispositivo 2FA confirmado
    device = next(devices_for_user(user, confirmed=True), None)

    if device:
        # Se tiver, inicia o processo de login com OTP, passando o DISPOSITIVO.
        otp_login(request, device)  # <-- CORREÇÃO APLICADA AQUI

        # Guarda na sessão que uma verificação de 2FA está pendente.
        request.session['2fa_pending_verification'] = True
