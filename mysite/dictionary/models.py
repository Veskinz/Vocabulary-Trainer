from django.db import models
    
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    
class Words(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=30)
    rightAnswer = models.CharField(max_length=1)
    wrongAnswer = models.CharField(max_length=1)
