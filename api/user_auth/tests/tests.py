# tests/test_serializers.py

from django.test import TestCase
from ..serializers import RegisterSerializer
from factories.factories import UserFactory


class RegisterSerializerTest(TestCase):

    def setUp(self):
        self.valid_payload = {
            'username': 'newuser',
            'password': 'password123'
        }

    def test_register_user_success(self):
        """Test successful user registration and access token generation."""
        serializer = RegisterSerializer(data=self.valid_payload)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.username, 'newuser')

        representation = serializer.to_representation(user)
        self.assertIn('access', representation)
        self.assertIsNotNone(representation['access'])

    def test_register_user_username_already_exists(self):
        """Test registration with an existing username."""
        UserFactory(username='existinguser', password='password123')
        self.valid_payload['username'] = 'existinguser'
        serializer = RegisterSerializer(data=self.valid_payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
