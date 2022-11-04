from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView, logout_then_login
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-then-login/', logout_then_login, name='logout-then-login'),
    path('register/', views.register, name='register'),
    path('',views.profile, name = 'user_profile'),
    path('edit/',views.profile_edit, name = 'edit_profile'),

        ]
