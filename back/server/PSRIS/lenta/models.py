from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
from PIL import Image

class Post(models.Model):
    title = models.CharField(blank = True, max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title



def get_image_filename(instance, filename):
    title = instance.post.title
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename)  


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, default=None)
    image = models.ImageField(upload_to='post_pics',
                              verbose_name='image',
                              )
def save(self, *args, **kwargs):
    super(PostImage, self).save(*args, **kwargs)

    img = Image.open(self.image.path)

    if img.height > 300 or img.width > 300:
        output_size = (300,300)
        img.thumbnail(output_size)
        img.save(self.image.path)