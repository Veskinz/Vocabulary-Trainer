from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Words

class UserSerializer(serializers.ModelSerializer):
    words = serializers.PrimaryKeyRelatedField(many=True, queryset=Words.objects.all())
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'words']

class WordsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    
    class Meta:
        model = Words
        fields = ['id', 'rightWord', 'wrongWord', 'username']