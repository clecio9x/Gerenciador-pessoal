import json
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import requests
import os
import secrets

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .forms import (
    LoginForm, RegisterForm, NoteForm, OTPTokenForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .models import PasswordEntry, Note, PasswordResetToken, Profile, TelegramLinkToken
from .services import (
    create_reset_token, send_reset_email,
    get_reset_token, invalidate_reset_token
)
from django_otp import devices_for_user, login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice

# ===================================================================
# VIEWS DE AUTENTICAÇÃO
# ===================================================================

# em cofre/views.py

from django.shortcuts import render, redirect
from django.contrib import auth
from .forms import LoginForm # Supondo que você tenha um LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = auth.authenticate(request, username=username, password=password)

            if user is not None:
                # VERIFICA SE O USUÁRIO TEM UM DISPOSITIVO 2FA ATIVADO
                device = next(devices_for_user(user, confirmed=True), None)

                if device:
                    # CASO 1: Usuário tem 2FA.
                    # NÃO faça login. Apenas prepare a sessão para a verificação do OTP.
                    request.session['_otp_user_id'] = user.pk
                    request.session['2fa_pending_verification'] = True
                    return redirect('otp_verify') # Redireciona para sua view de verificação
                else:
                    # CASO 2: Usuário NÃO tem 2FA.
                    # Faça o login normalmente.
                    auth.login(request, user)
                    messages.success(request, f'Bem-vindo(a), {user.username}!')
                    return redirect('dashboard')
            else:
                # Credenciais inválidas. Adiciona uma mensagem de erro.
                messages.error(request, 'Usuário ou senha inválidos. Por favor, tente novamente.')
    else:
        form = LoginForm()

    # Renderiza o formulário novamente em caso de GET ou falha de validação
    return render(request, 'login.html', {'form': form})

def otp_verify_view(request):
    """
    View de verificação de OTP à prova de loops.
    """
    user = None
    user_id = request.session.get('_otp_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

    if not user and request.user.is_authenticated:
        user = request.user

    if not user:
        if '2fa_pending_verification' in request.session:
            del request.session['2fa_pending_verification']
        if '_otp_user_id' in request.session:
            del request.session['_otp_user_id']
        return redirect('login')

    device = next(devices_for_user(user, confirmed=True), None)
    if not device:
        if '2fa_pending_verification' in request.session:
            del request.session['2fa_pending_verification']
        return redirect('dashboard')

    if request.method == 'POST':
        form = OTPTokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('token')
            if device.verify_token(token):
                # Guarda o usuário antes de limpar a sessão
                user_to_login = device.user
                
                # Faz o login completo, que também rotaciona a sessão
                login(request, user_to_login, backend='django.contrib.auth.backends.ModelBackend')

                # Limpa as flags de OTP explicitamente da nova sessão
                if '2fa_pending_verification' in request.session:
                    del request.session['2fa_pending_verification']
                if '_otp_user_id' in request.session:
                    del request.session['_otp_user_id']
                
                return redirect('dashboard')
            else:
                form.add_error(None, 'Código inválido. Tente novamente.')
    else:
        form = OTPTokenForm()

    return render(request, 'otp_verify.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Registro bem-sucedido! Bem-vindo(a).')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ===================================================================
# VIEWS DE RESET DE SENHA
# ===================================================================

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                reset_token = create_reset_token(user)
                send_reset_email(user, reset_token)
            except User.DoesNotExist:
                pass
            messages.success(request, 'Se o email existir em nossa base, você receberá um link de recuperação.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {'form': form})


def password_reset_done(request):
    return render(request, 'password_reset_done.html')


def password_reset_confirm(request, token):
    reset_token = get_reset_token(token)
    if not reset_token:
        messages.error(request, 'Link de recuperação inválido ou expirado.')
        return redirect('password_reset_request')
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            invalidate_reset_token(reset_token)
            messages.success(request, 'Senha alterada com sucesso! Você pode fazer login agora.')
            return redirect('login')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'password_reset_confirm.html', {'form': form, 'token': token})


# ===================================================================
# VIEWS DE PÁGINA E CONTEÚDO
# ===================================================================

@login_required
def dashboard(request):
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'dashboard.html', {'notes': notes})


@login_required
def note_editor_view(request, note_id=None):
    note = None
    if note_id:
        note = get_object_or_404(Note, id=note_id, user=request.user)
    return render(request, 'note_editor.html', {'note': note})


# ===================================================================
# API PARA SENHAS
# ===================================================================

@login_required
def password_api_list(request):
    passwords = PasswordEntry.objects.filter(user=request.user)
    data = [{'id': p.id, 'title': p.title} for p in passwords]
    return JsonResponse(data, safe=False)


@login_required
def password_api_retrieve(request, entry_id):
    entry = get_object_or_404(PasswordEntry, id=entry_id, user=request.user)
    decrypted_password = entry.get_password()
    return JsonResponse({'password': decrypted_password})


@login_required
def password_api_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        password = data.get('password')
        if not title or not password:
            return JsonResponse({'error': 'Título e senha são obrigatórios'}, status=400)
        entry = PasswordEntry(user=request.user, title=title)
        entry.set_password(password)
        entry.save()
        return JsonResponse({'status': 'success', 'id': entry.id, 'title': entry.title}, status=201)
    return JsonResponse({'error': 'Método inválido'}, status=405)


@login_required
def password_api_delete(request, entry_id):
    if request.method == 'DELETE':
        entry = get_object_or_404(PasswordEntry, id=entry_id, user=request.user)
        entry.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Método inválido'}, status=405)


# ===================================================================
# API PARA NOTAS
# ===================================================================

@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('dashboard')
    else:
        form = NoteForm()
    return render(request, 'note_form.html', {'form': form})


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = NoteForm(instance=note)
    return render(request, 'note_form.html', {'form': form})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('dashboard')
    return render(request, 'note_confirm_delete.html', {'note': note})


# ===================================================================
# VIEW DE SETUP DO 2FA
# ===================================================================

@login_required
def two_factor_setup(request):
    user = request.user
    existing_device = next(devices_for_user(user, confirmed=True), None)
    context = {'device': existing_device}
    if request.method == 'POST':
        if 'disable_2fa' in request.POST and existing_device:
            existing_device.delete()
            return redirect('2fa_setup')
        if 'enable_2fa' in request.POST:
            code = request.POST.get('code')
            unconfirmed_device_id = request.session.get('2fa_device_id')
            if not unconfirmed_device_id:
                return redirect('2fa_setup')
            try:
                device_to_confirm = TOTPDevice.objects.get(id=unconfirmed_device_id, user=user)
                if device_to_confirm.verify_token(code):
                    device_to_confirm.confirmed = True
                    device_to_confirm.save()
                    del request.session['2fa_device_id']
                    return redirect('2fa_setup')
                else:
                    context['error'] = 'Código inválido. Tente novamente.'
                    img = qrcode.make(device_to_confirm.config_url, image_factory=qrcode.image.svg.SvgImage)
                    buffer = BytesIO()
                    img.save(buffer)
                    context['qr_code'] = base64.b64encode(buffer.getvalue()).decode()
            except TOTPDevice.DoesNotExist:
                return redirect('2fa_setup')
    else:
        if not existing_device:
            TOTPDevice.objects.filter(user=user, confirmed=False).delete()
            device_to_confirm = TOTPDevice.objects.create(user=user, confirmed=False)
            request.session['2fa_device_id'] = device_to_confirm.id
            img = qrcode.make(device_to_confirm.config_url, image_factory=qrcode.image.svg.SvgImage)
            buffer = BytesIO()
            img.save(buffer)
            context['qr_code'] = base64.b64encode(buffer.getvalue()).decode()
    return render(request, '2fa_setup.html', context)

# ===================================================================
# VIEW DE SETUP DO BOT TELEGRAM
# ===================================================================


@csrf_exempt
@require_POST
def telegram_note_receiver(request):
    # Validação da chave de API (continua igual e correta)
    auth_header = request.headers.get('Authorization')
    secret_key = os.getenv('TELEGRAM_API_KEY')
    if not auth_header or auth_header != f'Bearer {secret_key}':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)

        chat_id = data.get('chat_id')
        content = data.get('content')

        if not chat_id or not content:
            return JsonResponse({'status': 'error', 'message': 'Dados ausentes'}, status=400)

        try:
            profile = Profile.objects.get(telegram_chat_id=str(chat_id))
            user = profile.user
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuário do Telegram não vinculado. Use o comando /vincular.'}, status=404)
        
        # Cria a nota para o usuário encontrado
        Note.objects.create(user=user, title="Nota do Telegram", content=content)
        
        return JsonResponse({'status': 'success', 'message': 'Nota criada com sucesso!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
# ===================================================================
# VIEW DE LOGIN DO BOT TELEGRAM
# ===================================================================
        
        
@login_required
def link_telegram_view(request):
    # Deleta tokens antigos do usuário para gerar um novo
    TelegramLinkToken.objects.filter(user=request.user).delete()
    
    # Gera um novo token de 8 caracteres
    token_str = secrets.token_hex(4).upper()
    
    # Salva o novo token no banco de dados
    new_token = TelegramLinkToken.objects.create(user=request.user, token=token_str)
    
    context = {
        'token': new_token.token,
    }
    return render(request, 'link_telegram.html', context)


@csrf_exempt
@require_POST
def link_telegram_api(request):
    # Valida a chave de API (mesma da outra função)
    auth_header = request.headers.get('Authorization')
    secret_key = os.getenv('TELEGRAM_API_KEY')
    if not auth_header or auth_header != f'Bearer {secret_key}':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=401)
        
    try:
        data = json.loads(request.body)
        token = data.get('token')
        chat_id = data.get('chat_id')

        if not token or not chat_id:
            return JsonResponse({'status': 'error', 'message': 'Token ou chat_id ausente'}, status=400)

        # Procura pelo token no banco de dados
        link_token = TelegramLinkToken.objects.get(token=token)
        
        # Se encontrou, atualiza o perfil do usuário com o chat_id
        user_profile = link_token.user.profile
        user_profile.telegram_chat_id = chat_id
        user_profile.save()
        
        # Deleta o token para que não possa ser usado novamente
        link_token.delete()
        
        return JsonResponse({'status': 'success', 'message': f'Conta de {link_token.user.username} vinculada com sucesso!'})

    except TelegramLinkToken.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Token inválido ou expirado.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
@require_POST
def unlink_telegram_api(request):
    # Validação da chave de API (reutilizamos a mesma lógica)
    auth_header = request.headers.get('Authorization')
    secret_key = os.getenv('TELEGRAM_API_KEY')
    if not auth_header or auth_header != f'Bearer {secret_key}':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')

        if not chat_id:
            return JsonResponse({'status': 'error', 'message': 'chat_id ausente'}, status=400)

        # Encontra o perfil pelo chat_id
        profile = Profile.objects.get(telegram_chat_id=str(chat_id))
        
        # Remove a associação
        profile.telegram_chat_id = None
        profile.save()
        
        return JsonResponse({'status': 'success', 'message': 'Conta desvinculada com sucesso.'})

    except Profile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Esta conta do Telegram não está vinculada.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
