from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView, logout_then_login
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-then-login/', logout_then_login, name='logout-then-login'),
    path('register/', views.register, name='register'),
    path('edit/<str:username>',views.profile_edit, name = 'edit_profile'),
    path('<str:username>', views.UserPostListView.as_view(), name = 'user_profile'),
    

        ]
