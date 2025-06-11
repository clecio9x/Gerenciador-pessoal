from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def login_view(request):
    # Se já está logado, vai direto pro dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'cofre/login.html', {'error': 'Usuário ou senha incorretos.'})
    
    return render(request, 'cofre/login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'cofre/dashboard.html', {'username': request.user.username})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'cofre/register.html', {'error': 'Usuário já existe.'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')
    
    return render(request, 'cofre/register.html')


@csrf_exempt
def save_secret(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tipo = data.get('type')
        titulo = data.get('title')
        valor = data.get('value')

        print(f"Salvando {tipo} - {titulo}: {valor}")
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Método não suportado'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('login')
