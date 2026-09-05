from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def test_register_user_success(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123!',
            'confirm_password': 'testpass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check user was created with correct data
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123!'))

    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpass123!',
            'confirm_password': 'differentpass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='testuser2').exists())

    def test_register_user_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create first user
        User.objects.create_user(
            username='testuser',
            email='first@example.com',
            password='testpass123!'
        )
        
        # Try to create second user with same username
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'second@example.com',
            'password': 'testpass123!',
            'confirm_password': 'testpass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create first user
        User.objects.create_user(
            username='testuser1',
            email='test@example.com',
            password='testpass123!'
        )
        
        # Try to create second user with same email
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testpass123!',
            'confirm_password': 'testpass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jwtuser',
            email='jwt@example.com',
            password='jwtpass123!',
            first_name='JWT',
            last_name='User'
        )

    def test_login_success(self):
        """Test successful login and token generation"""
        url = reverse('login')
        data = {'username': 'jwtuser', 'password': 'jwtpass123!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.cookies)
        self.assertEqual(response.data['user']['username'], 'jwtuser')

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        url = reverse('login')
        data = {'username': 'jwtuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh functionality using refresh_token cookie"""
        login_url = reverse('login')
        login_data = {'username': 'jwtuser', 'password': 'jwtpass123!'}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.cookies['refresh_token'].value
        
        refresh_url = reverse('token_refresh')
        self.client.cookies['refresh_token'] = refresh_token
        refresh_response = self.client.post(refresh_url)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', refresh_response.data)


    def test_token_refresh_missing_cookie_fails(self):
        """Test token refresh fails with 401 when refresh cookie is missing"""
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_cors_preflight_allowed_origin_returns_credentials_header(self):
        """Test CORS preflight returns Access-Control-Allow-Credentials for allowed origin"""
        url = reverse('login')
        response = self.client.options(
            url,
            HTTP_ORIGIN='http://localhost:5173',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), 'http://localhost:5173')
        self.assertEqual(response.headers.get('Access-Control-Allow-Credentials'), 'true')
    def test_get_current_user_authenticated(self):
        """Test GET /api/users/me/ returns authenticated user's details"""
        url = reverse('me')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], 'jwtuser')
        self.assertEqual(response.data['email'], 'jwt@example.com')
        self.assertEqual(response.data['first_name'], 'JWT')
        self.assertEqual(response.data['last_name'], 'User')

    def test_get_current_user_unauthenticated(self):
        """Test GET /api/users/me/ fails when not authenticated"""
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class UserModelTests(APITestCase):
    def test_user_creation(self):
        """Test user model creation"""
        user = User.objects.create_user(
            username='modeltest',
            email='model@example.com',
            password='testpass123!',
            first_name='Model',
            last_name='Test'
        )
        self.assertEqual(user.username, 'modeltest')
        self.assertEqual(user.email, 'model@example.com')
        self.assertTrue(user.check_password('testpass123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_string_representation(self):
        """Test user __str__ method"""
        user = User.objects.create_user(
            username='strtest',
            email='str@example.com',
            password='testpass123!'
        )
        self.assertEqual(str(user), 'strtest')

    def test_user_get_full_name(self):
        """Test user get_full_name method"""
        user = User.objects.create_user(
            username='fullnametest',
            email='fullname@example.com',
            password='testpass123!',
            first_name='Full',
            last_name='Name'
        )
        self.assertEqual(user.get_full_name(), 'Full Name')
        
        # Test with empty names
        user_no_name = User.objects.create_user(
            username='nonametest',
            email='noname@example.com',
            password='testpass123!'
        )
        self.assertEqual(user_no_name.get_full_name(), 'nonametest')

    def test_superuser_creation(self):
        """Test superuser creation"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123!'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_active)