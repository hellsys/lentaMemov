from django.urls import path
from .views import (
    # PostCreateView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    like_view,
    skip_view
)
from . import views

urlpatterns = [
    path('', views.lenta, name='lenta'),
    path('post/new/', views.createPost, name='post-create'),
    path('post/<int:pk>/update/', views.post_update, name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/like/<int:pk>/', like_view, name='post-like'),
    path('post/skip/', skip_view, name='post-skip'),

]
