from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, PostImage
from .forms import PostForm, ImageForm
from django.contrib.auth.models import User
from django.db.models import Q

def lenta(request):
    post_ = Post.objects.filter(~Q(author_id=request.user)).order_by("?").first()
    images = PostImage.objects.filter(post_id=post_.id)
    context = {'object': post_,
                'images': images}
    return render(request, 'lenta/lenta.html', context)

def createPost(request):
    form = PostForm()
    form2 = ImageForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        form.instance.author = request.user
        images = request.FILES.getlist('image')
        form2 = ImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            post_inst = Post.objects.create(
                title=title, content=content, author=request.user)
            

            for i in images:
                print('olo')
                PostImage.objects.create(post=post_inst, image=i)
                    

    context = {'form': form, 'form2': form2}
    return render(request, 'lenta/post_create_form.html', context)



class PostDetailView(DetailView):
    model = Post


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name_suffix = '_update'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_success_url(self):
        url = f'/account/{self.request.user.username}'
        return url



class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



class UserPostListView(ListView):
    model = Post
    template_name = 'lenta/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        posts_ = Post.objects.filter(author=user).order_by('-date_posted')  
        images = [PostImage.objects.filter(post_id=i.id) for i in posts_]
        context={
            'author': user,
            'posts' : posts_,
            'images_list' : images,
            'count' : len(posts_)

        }
        print(posts_)
        return context 