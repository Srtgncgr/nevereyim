from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Mevcut URL'ler
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Yeni adres URL'leri
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Mevcut URL'ler...
    path('update-user-info/', views.update_user_info, name='update_user_info'),
    path('change-password/', views.change_password, name='change_password'),
]