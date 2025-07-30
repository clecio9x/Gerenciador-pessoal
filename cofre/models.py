from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets


class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_items')
    title = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"



class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


def encrypt_password(password):
    f = Fernet(settings.FERNET_KEY)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    f = Fernet(settings.FERNET_KEY)
    return f.decrypt(encrypted_password.encode()).decode()

# --- Modelo para Senhas Salvas ---
class PasswordEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    encrypted_password = models.TextField() # Guardamos a senha criptografada
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.encrypted_password = encrypt_password(password)

    def get_password(self):
        return decrypt_password(self.encrypted_password)

    def __str__(self):
        return self.title

# --- Modelo para Reset de Senha ---
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        """Verifica se o token ainda é válido (24 horas)"""
        from django.utils import timezone
        from datetime import timedelta
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=24)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"
        
        
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

# Este "sinal" garante que um Perfil seja criado automaticamente para cada novo Usuário
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class TelegramLinkToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Token para {self.user.username}'
