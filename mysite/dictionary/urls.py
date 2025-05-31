from django.urls import path
from .views import SignUpView, LoginView, UserWordsView, WordDetailView, WordTestView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('words/', UserWordsView.as_view(), name='words'),
    path('words/test/', WordTestView.as_view(), name='test'),
    path('words/<int:pk>/', WordDetailView.as_view(), name='word_detail'),
]