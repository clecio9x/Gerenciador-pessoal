import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import PasswordResetToken

def generate_reset_token():
    """Gera um token seguro para reset de senha"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def create_reset_token(user):
    """Cria um novo token de reset para o usuário"""
    # Remove tokens antigos do usuário
    PasswordResetToken.objects.filter(user=user).delete()
    
    # Cria novo token
    token = generate_reset_token()
    reset_token = PasswordResetToken.objects.create(user=user, token=token)
    return reset_token

def send_reset_email(user, reset_token):
    """Envia email de reset de senha"""
    reset_url = f"{settings.SITE_URL}/password-reset/confirm/{reset_token.token}/"
    
    # Contexto para o template
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'KeyCrypt'
    }
    
    # Renderiza o template HTML
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    # Envia o email
    send_mail(
        subject='Recuperação de Senha - KeyCrypt',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def get_reset_token(token_string):
    """Busca um token de reset válido"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token_string)
        if reset_token.is_valid():
            return reset_token
    except PasswordResetToken.DoesNotExist:
        pass
    return None

def invalidate_reset_token(reset_token):
    """Marca um token como usado"""
    reset_token.used = True
    reset_token.save()
