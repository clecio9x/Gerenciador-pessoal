from django.contrib import admin
from django.urls import path, include
from cofre import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cofre.urls')),
     path('api/notes/', views.NoteAPIListView.as_view(), name='note_api_list'),
    path('accounts/', include('allauth.urls')),
]