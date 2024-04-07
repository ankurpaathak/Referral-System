from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User, Referrals
from rest_framework.authtoken.models import Token


class RegistrationTests(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)
        self.assertIn('message', response.data)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', password='password123')

    def test_login(self):
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('created_at', response.data)

class UserDetailsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', password='password123')

    def test_user_details(self):
        self.client.force_login(self.user)
        url = reverse('UserDetails')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('referral_code', response.data)
        self.assertIn('created_at', response.data)

class UserReferralsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', password='password123')

    def test_user_referrals(self):
        self.client.force_login(self.user)
        url = reverse('UserReferrals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', password='password123')
        self.token = Token.objects.create(user=self.user)

    def test_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='token ' + self.token.key)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
