from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email
    
class Video(models.Model):
    title = models.CharField(max_length=255)
    news_url = models.URLField(max_length=500, null=True)
    news_title = models.TextField(null=True)
    news_content = models.TextField(null=True)
    script = models.TextField(null=True)
    config = models.TextField(null=True)  # Will store JSON as string
    # URL will just be an endpoint based on the video id
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')

    def __str__(self):
        return self.title
    

    
