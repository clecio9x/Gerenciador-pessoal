from django.contrib import admin
from django.urls import path, include
from cofre import views

urlpatterns = [
    path('admin/', admin.site.urls),
#    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    path('accounts/', include('allauth.urls')),
#    path('register/', views.register_view, name='register'),
#    path('login/', views.login_view, name='login'),
 #   path('logout/', views.logout_view, name='logout'),
#    path('dashboard/', views.dashboard, name='dashboard'),
    path('', include('cofre.urls')),
]
