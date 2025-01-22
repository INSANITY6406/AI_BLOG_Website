from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class blog_post(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    yt_Title=models.CharField( max_length=300)
    yt_url=models.URLField()
    generated_content=models.TextField()
    create_time=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.yt_Title