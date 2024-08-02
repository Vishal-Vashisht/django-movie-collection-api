# tests/test_views.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.cache import caches

cache_ = caches['default']


class RequestCountAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = 'username'
        self.password = 'password'

        token_url = reverse('register')

        response = self.client.post(token_url, {'username': self.username,
                                                'password': self.password})
        self.token = response.data['access']

        # Set the Authorization header for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        cache_.set('request_count', 10)  # Setting initial request count

    def test_get_request_count_success(self):
        url = reverse('request-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['requests'], 11)

    def test_reset_request_count_success(self):
        url = reverse('reset-request-count')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Request count reset successfully") # noqa
        self.assertEqual(cache_.get('request_count'), 0)

    def test_get_request_count_unauthorized(self):
        self.client.credentials()
        url = reverse('request-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_request_count_unauthorized(self):
        self.client.credentials() 
        url = reverse('reset-request-count')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
