from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Words
from .serializers import UserSerializer, WordsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404
import random


class SignUpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User(username=serializer.validated_data['username'])
            user.set_password(serializer.validated_data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserWordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        words = request.user.words.all()
        serializer = WordsSerializer(words, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = WordsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Words, pk=pk, user=user)

    def get(self, request, pk, format=None):
        word = self.get_object(pk, request.user)
        serializer = WordsSerializer(word)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        word = self.get_object(pk, request.user)
        serializer = WordsSerializer(word, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        word = self.get_object(pk, request.user)
        word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  

class WordTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        words = list(request.user.words.all())
        if not words:
            return Response({"detail": "Нямате добавени думи за тест."}, status=status.HTTP_400_BAD_REQUEST)

        selected_words = random.sample(words, min(20, len(words)))

        request.session['test_words'] = [word.id for word in selected_words]
        request.session['test_index'] = 0
        request.session['correct_answers'] = 0
        request.session['last_answer_correct'] = None
        request.session.modified = True

        return self.next_word_response(request)

    def post(self, request, format=None):
        test_words_ids = request.session.get('test_words', [])
        test_index = request.session.get('test_index', 0)
        correct_answers = request.session.get('correct_answers', 0)

        if test_index >= len(test_words_ids):
            return Response({"detail": "The test has ended."}, status=status.HTTP_400_BAD_REQUEST)

        word = get_object_or_404(Words, pk=test_words_ids[test_index], user=request.user)

        user_answer = request.data.get("answer")
        is_correct = user_answer == word.rightWord

        if is_correct:
            correct_answers += 1
        
        request.session['last_answer_correct'] = is_correct

        request.session['test_index'] = test_index + 1
        request.session['correct_answers'] = correct_answers
        request.session.modified = True

        if test_index + 1 < len(test_words_ids):
            return self.next_word_response(request)
        else:
            score = correct_answers
            total = len(test_words_ids)
            request.session.flush()
            return Response({
                "last_answer_correct": is_correct,
                "detail": "Result:",
                "correct_answers": score,
                "total": total
            })

    def next_word_response(self, request):
        test_words_ids = request.session['test_words']
        test_index = request.session['test_index']
        word = get_object_or_404(Words, pk=test_words_ids[test_index], user=request.user)

        choices = [word.rightWord, word.wrongWord]
        random.shuffle(choices)

        last_answer_correct = request.session.get('last_answer_correct', None)

        return Response({
            "last_answer_correct": last_answer_correct,
            "question": "Which word is correct?",
            "choices": choices,
            "current": test_index + 1,
            "total": len(test_words_ids),
        })