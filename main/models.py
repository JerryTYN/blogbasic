from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse

# Create your models here.


    
    
def upload_path(instance, filename):
    return f'media/post_covers/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=upload_path)

    def __str__(self):
        return self.user.username if hasattr(self, 'user') else 'UserProfile'


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class AuthorFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image_cover = models.ImageField(upload_to=upload_path, null=True)
    title = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category)
    content = RichTextUploadingField()
    likes = models.ManyToManyField(User, related_name='blog_post')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    def number_of_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title + "\n" + self.description + "\n" + str(self.author) + self.id
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

class Comment(models.Model):
	post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	content=models.TextField()
	timestamp=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.post.title+self.user.username
