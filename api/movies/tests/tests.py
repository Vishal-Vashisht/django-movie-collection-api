from unittest.mock import patch

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from factories.factories import CollectionFactory, MovieFactory
from requests.models import Response
from rest_framework import status

from ..models import Collection
from ..serializers import CollectionSerializer
from ..services import MovieListService, UpdateCollectionService


class MovieListServiceTest(TestCase):

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_success(self, mock_get):

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"next": "/?page=2", "previous": null, "results": [{"id": 1, "title": "Movie 1"}]}'
        mock_get.return_value = mock_response

        class MockRequest:
            GET = {"page": "1"}

            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()

        response = MovieListService().get_list(request)

        self.assertIn('next', response)
        self.assertIn('previous', response)
        self.assertIn('results', response)
        self.assertEqual(response['results'][0]['title'], "Movie 1")

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_http_error(self, mock_get):

        mock_get.side_effect = requests.exceptions.HTTPError("HTTP error occurred")

        class MockRequest:
            GET = {"page": "1"}

            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()

        with self.assertRaises(requests.exceptions.HTTPError):
            MovieListService().get_list(request)

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_request_exception(self, mock_get):

        mock_get.side_effect = requests.RequestException("Request error occurred")

        class MockRequest:

            GET = {"page": "1"}

            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()

        with self.assertRaises(requests.RequestException):
            MovieListService().get_list(request)

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_no_movies(self, mock_get):

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"next": null, "previous": null, "results": []}'
        mock_get.return_value = mock_response

        class MockRequest:
            GET = {"page": "1"}
            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()
        response = MovieListService().get_list(request)

        self.assertEqual(response['results'], [])
        self.assertIsNone(response['next'])
        self.assertIsNone(response['previous'])

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_invalid_page(self, mock_get):

        mock_response = Response()
        mock_response.status_code = 404
        mock_response._content = b'{"error": "Page not found"}'
        mock_get.return_value = mock_response

        class MockRequest:
            GET = {"page": "999"}

            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()

        with self.assertRaises(requests.exceptions.HTTPError):
            MovieListService().get_list(request)

    @patch('api.utils.api_client.APIClient.get')
    def test_get_list_previous_page(self, mock_get):

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"next": "/?page=3", "previous": "/?page=1", "results": [{"id": 2, "title": "Movie 2"}]}'
        mock_get.return_value = mock_response

        class MockRequest:
            GET = {"page": "2"}
            def build_absolute_uri(self, path):
                return f"http://testserver{path}"

            @property
            def path(self):
                return "/movies/"

        request = MockRequest()
        response = MovieListService().get_list(request)

        self.assertIn('next', response)
        self.assertIn('previous', response)
        self.assertEqual(response['previous'], "http://testserver/movies/?page=1")


class ListCollectionsServiceTest(TestCase):
    def setUp(self):
        self.collection = CollectionFactory()

        self.movie1 = MovieFactory(collection=self.collection)
        self.movie2 = MovieFactory(collection=self.collection)

    def test_get_collections(self):
        collections = Collection.objects.prefetch_related('movies').all()
        self.assertEqual(collections.count(), 1)
        self.assertEqual(collections.first().movies.count(), 2)


class ListParticularCollectionsTest(TestCase):
    def setUp(self):
        self.collection = CollectionFactory()

        self.movie1 = MovieFactory(collection=self.collection)
        self.movie2 = MovieFactory(collection=self.collection)

    def test_get_collections_particular(self):
        collections = Collection.objects.prefetch_related('movies').get(uuid=self.collection.uuid)
        self.assertEqual(collections, self.collection)
        self.assertEqual(collections.movies.count(), 2)

    def test_invalid_collection_id(self):
        invalid_uuid = '12345678-1234-5678-1234-567812345679'

        with self.assertRaises(ObjectDoesNotExist):
            Collection.objects.get(uuid=invalid_uuid)


class CreateCollectionServiceTest(TestCase):

    # Static payload for collection data
    COLLECTION_DATA = {
        'title': 'Collection 1',
        'description': 'Test collection',
        'movies': [
            {
                'title': 'Movie 1',
                'description': 'Description for movie 1',
                'genres': 'Action',
                'uuid': '12345678-1234-5678-1234-567812345678',
            },
            {
                'title': 'Movie 2',
                'description': 'Description for movie 2',
                'genres': 'Drama',
                'uuid': '23456789-2345-6789-2345-678923456789',
            },
        ],
    }

    def setUp(self):

        self.collection_data = self.COLLECTION_DATA.copy()
        self.collection = CollectionFactory.create()

    def test_create_collection_with_movies(self):
        serializer = CollectionSerializer(data=self.collection_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        collection = serializer.save()

        # Check that the movies were created correctly
        self.assertEqual(collection.movies.count(), 2)
        self.assertEqual(collection.movies.first().title, self.collection_data['movies'][0]['title'])


class UpdateCollectionServiceTest(TestCase):

    def setUp(self):

        self.collection = CollectionFactory()

        self.movie = MovieFactory(collection=self.collection)

    def test_update_collection(self):

        update_data = {
            "title": "Updated Collection Title",
            "description": "Updated description",
            "movies": [
                {
                    "uuid": str(self.movie.uuid),
                    "title": "Movie 1",
                    "description": "Updated description for Movie 1",
                    "genres": "Action"
                }
            ]
        }

        serializer = CollectionSerializer(instance=self.collection, data=update_data)

        updated_collection = UpdateCollectionService().update_collections(serializer)

        self.assertEqual(updated_collection['title'], "Updated Collection Title")
        self.assertEqual(updated_collection['description'], "Updated description")
        self.assertEqual(len(updated_collection['movies']), 1)
        self.assertEqual(updated_collection['movies'][0]['title'], "Movie 1")


class DeleteCollectionTest(APITestCase):

    def setUp(self):

        self.username = 'username'
        self.password = 'password'
        token_url = reverse('register')
        response = self.client.post(token_url, {'username': self.username,
                                                'password': self.password})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.collection = CollectionFactory.create()

        self.url = reverse('collection-detail',
                           kwargs={'pk': self.collection.uuid})

    def test_delete_collection(self):
        response = self.client.delete(self.url)

        # Ensure the response status code is 204 No Content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the collection is actually deleted
        self.assertFalse(Collection.objects.filter(
            uuid=self.collection.uuid).exists())

    def test_delete_invalid_collection(self):
        # Generate an invalid UUID that doesn't correspond to any collection
        invalid_uuid = '12345678-1234-5678-1234-567812345679'
        url = reverse('collection-detail', args=[invalid_uuid])

        response = self.client.delete(url)

        # Check that the response status is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)