from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jwtuser', password='jwtpass123', email='jwt@example.com'
        )

    def test_token_obtain_pair(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'jwtuser', 'password': 'jwtpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)