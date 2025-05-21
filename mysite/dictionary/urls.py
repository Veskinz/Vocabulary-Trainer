from django.urls import path
from .views import SignUpView, LoginView, UserWordsView, WordDetailView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('userwords/', UserWordsView.as_view(), name='userwords'),
    path('userwords/<int:pk>/', WordDetailView.as_view(), name='word_detail'),
]