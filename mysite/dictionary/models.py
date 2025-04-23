from django.db import models
from django.contrib.auth.models import User
    
class Words(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rightWord = models.CharField(max_length=30)
    wrongWord = models.CharField(max_length=30)