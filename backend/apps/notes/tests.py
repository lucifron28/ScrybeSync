from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Note

User = get_user_model()

class CategoryModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password123'
        )

    def test_different_users_can_have_same_category_name(self):
        cat1 = Category.objects.create(name='School', user=self.user1)
        cat2 = Category.objects.create(name='School', user=self.user2)
        self.assertEqual(cat1.name, cat2.name)
        self.assertNotEqual(cat1.user, cat2.user)

    def test_same_user_cannot_have_duplicate_category_name_db(self):
        Category.objects.create(name='School', user=self.user1)
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='School', user=self.user1)


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password123'
        )
        self.url = reverse('category-list')

    def test_different_users_can_create_same_category_via_api(self):
        self.client.force_authenticate(user=self.user1)
        res1 = self.client.post(self.url, {'name': 'School', 'description': 'User 1 school'})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.user2)
        res2 = self.client.post(self.url, {'name': 'School', 'description': 'User 2 school'})
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

    def test_same_user_cannot_create_duplicate_category_via_api(self):
        self.client.force_authenticate(user=self.user1)
        res1 = self.client.post(self.url, {'name': 'School', 'description': 'First'})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post(self.url, {'name': 'School', 'description': 'Second'})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res2.data)


class NoteCategoryOwnershipAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password123'
        )
        self.cat1 = Category.objects.create(name='User1 Category', user=self.user1)
        self.cat2 = Category.objects.create(name='User2 Category', user=self.user2)
        self.notes_url = reverse('note-list')

    def test_user_can_assign_own_category(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post(self.notes_url, {
            'title': 'User 1 Note',
            'content': 'Note content',
            'category': self.cat1.id
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['category'], self.cat1.id)

    def test_user_cannot_assign_another_users_category_on_create(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post(self.notes_url, {
            'title': 'Unauthorized category test',
            'content': 'Attempting to use user2 category',
            'category': self.cat2.id
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', res.data)

    def test_user_cannot_assign_another_users_category_on_update(self):
        self.client.force_authenticate(user=self.user1)
        note = Note.objects.create(
            title='Initial Note',
            content='Initial Content',
            category=self.cat1,
            user=self.user1
        )
        detail_url = reverse('note-detail', kwargs={'pk': note.id})
        res = self.client.patch(detail_url, {
            'category': self.cat2.id
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', res.data)
