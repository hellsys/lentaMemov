from django import forms
from .models import Post, PostImage
from django.forms.widgets import ClearableFileInput

class MyClearableFileInput(ClearableFileInput):
    template_name = 'forms/widgets/custom.html'
    #
    # def render(self, name, value, attrs=None):
    #     context = self.get_context(name, value, attrs)
    #     template = loader.get_template(self.template_name).render(context)
    #     return mark_safe(template)

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=100, required=False, label='Title (не обязательно)')
    content = forms.CharField(max_length=100000, widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ['title', 'content']


class ImageForm(forms.ModelForm):
    # image = forms.ImageField(label='Image')    

    class Meta:
        model = PostImage
        fields = ('image', )
        widgets = {
            'image': MyClearableFileInput(attrs={'multiple': True}),
        }
