from django import forms
from .models import Post, PostImage

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
            'image': forms.ClearableFileInput(attrs={'multiple': True, 'name':'images'}),
        }

