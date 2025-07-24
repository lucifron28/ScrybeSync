from rest_framework import generics, permissions
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer 


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
