from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic.detail import DetailView

from .forms import LoginForm, UserRegisterForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

from lenta.models import Post, PostImage
from lenta.forms import PostForm, ImageForm
from django.contrib.auth.models import User


from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

@login_required
def profile(request):
    return render(request, 'account/user_profile.html')

@login_required
def profile_edit(request, **kwargs):    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect(f'/account/{request.user.username}')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'account/edit_profile.html', context)

class UserPostListView(ListView):
    model = Post
    template_name = 'account/user_profile.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        posts_ = Post.objects.filter(author=user).order_by('-date_posted')  
        images = [PostImage.objects.filter(post_id=i.id) for i in posts_]
        context={
            'posts' : posts_,
            'images_list' : images,
            'count' : len(posts_)

        }
        print(posts_)
        return context 





def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            user.save()
            profile = Profile()
            profile.user = user
            profile.save()
            messages.success(request, f'Ваш аккаунт создан: можно войти на сайт.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'account/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('%s'%(request.past))

