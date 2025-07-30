# cofre/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- ROTAS DE AUTENTICAÇÃO E PÁGINAS PRINCIPAIS ---
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- ROTAS PARA AS PÁGINAS DE NOTAS ---
    path('note/create/', views.note_editor_view, name='note_create'),
    #path('note/<int:note_id>/edit/', views.note_editor_view, name='note_edit'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    
    # --- ROTAS DA API DE SENHAS ---
    path('api/passwords/', views.password_api_list, name='password_api_list'),
    path('api/passwords/create/', views.password_api_create, name='password_api_create'),
    path('api/passwords/<int:entry_id>/', views.password_api_retrieve, name='password_api_retrieve'),
    path('api/passwords/<int:entry_id>/delete/', views.password_api_delete, name='password_api_delete'),

    # --- ROTAS DA API DE NOTAS ---
    path('notes/new/', views.note_create, name='note_create'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    # --- ROTAS DA API DE 2FA ---
    path('2fa/setup/', views.two_factor_setup, name='2fa_setup'),
    path('otp/verify/', views.otp_verify_view, name='otp_verify'),
    
    # --- ROTAS DE RESET DE SENHA ---
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    # --- ROTAS DA API DO TELEGRAM ---
    path('api/telegram/create-note/', views.telegram_note_receiver, name='telegram_note_receiver'),
    path('api/telegram/link-account/', views.link_telegram_api, name='link_telegram_api'),
    path('api/telegram/unlink-account/', views.unlink_telegram_api, name='unlink_telegram_api'),
    path('telegram/link/', views.link_telegram_view, name='link_telegram_view'),



]
