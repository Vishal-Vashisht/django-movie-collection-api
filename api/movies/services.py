from collections import Counter
from typing import Any, Dict, List

import requests
from api.utils.api_client import APIClient
from django.conf import settings
from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest
from dotenv import load_dotenv
from rest_framework.response import Response

from .models import Movie
from .serializers import MovieSerializer

load_dotenv()


class MovieListService:

    def get_list(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Fetches a list of movies from the external API.

        Args:
            request (HttpRequest): The HTTP request containing pagination information.

        Returns:
            Dict[str, Any]: A dictionary containing validated movie data.

        Raises:
            RequestException: If there is a network-related error.
            HTTPError: If the response from the API indicates an error.
            Exception: For any other exceptions that may occur.
        """ # noqa
        api_client = APIClient(
            base_url=settings.MOVIE_API,
            username=settings.MOVIE_API_USERNAME,
            password=settings.MOVIE_API_PASSWORD,
        )
        page = int(request.GET.get("page", 1))
        try:
            api_response = api_client.get(f"/?page={page}")
            return MovieListService.extract_validated_data(
                api_response, page, request)

        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
            Exception,
        ) as e:
            raise e

    @staticmethod
    def extract_validated_data(api_response: Response,
                               page: int,
                               request: HttpRequest) -> Dict[str, Any]:
        """
        Extracts and validates data from the API response.

        Args:
            api_response (Response): The response object from the API client.
            page (int): The current page number.
            request (HttpRequest): The HTTP request for further processing.

        Returns:
            Dict[str, Any]: A dictionary containing validated data.
        """
        status_code = api_response.status_code
        if status_code == 200:
            return MovieListService.build_response(api_response, page, request)
        else:
            if 'error' in api_response.json():

                error_response = Response()
                error_response.status_code = api_response.status_code
                error_response._content = api_response.content
                raise requests.exceptions.HTTPError(
                    api_response.json().get("error", "An error occurred"),
                    response=error_response
                )

    @staticmethod
    def build_response(response: Response,
                       page: int, request: HttpRequest) -> Dict[str, Any]:
        """
        Builds a response dictionary with pagination information.

        Args:
            response (Response): The response object from the API client.
            page (int): The current page number.
            request (HttpRequest): The HTTP request for constructing absolute URLs.

        Returns:
            Dict[str, Any]: A dictionary containing the API response data with pagination links.
        """ # noqa
        previous_page = next_page = None
        data = response.json()
        next_url = data.get("next")
        if next_url:
            next_page = f"{request.build_absolute_uri(request.path)}?page={page + 1}"  # noqa

        prev_url = data.get("previous")
        if prev_url and page > 1:
            previous_page = (
                f"{request.build_absolute_uri(request.path)}?page={page - 1}"
            )

        data["next"] = next_page
        data["previous"] = previous_page

        return data


class ListCollectionsService:

    def get_collections(self, queryset: QuerySet) -> Dict[str, Any]:
        """
        Retrieves collections along with their favorite genres.

        Args:
            queryset (QuerySet): A queryset of collections to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the success status and the collections with favorite genres.
        """ # noqa
        movies_prefetch = Prefetch("movies", queryset=Movie.objects.all())

        collections = queryset.prefetch_related(movies_prefetch).values(
            "uuid", "title", "description"
        )

        favorite_genres = ListCollectionsService.get_fav_gener(
            collections, queryset, movies_prefetch
        )

        response = {
            "is_success": True,
            "data": {
                "collections": collections,
                "favourite_genres": favorite_genres,
            },
        }

        return response

    @staticmethod
    def get_fav_gener(collections: List[Dict[str, Any]],
                      queryset: QuerySet,
                      movies_prefetch: Prefetch) -> List[str]:
        """
        Determines the favorite genres from the collections.

        Args:
            collections (List[Dict[str, Any]]): A list of collections.
            queryset (QuerySet): A queryset of collections to retrieve movies from.
            movies_prefetch (Prefetch): Prefetch object to optimize movie retrieval.

        Returns:
            List[str]: A list of the top three favorite genres.
        """ # noqa
        collections = list(collections)

        # Extract all genres
        all_genres = []
        for collection in queryset.prefetch_related(movies_prefetch):
            for movie in collection.movies.all():
                all_genres.extend(movie.genres.split(", "))

        # Get favorite genres
        favorite_genres = Counter(all_genres).most_common(3)
        favorite_genres = [genre[0] for genre in favorite_genres]

        return favorite_genres


class CreateCollectionService:

    def create_collection(self, serializer: object) -> Dict[str, str]:
        """
        Creates a new collection using the provided serializer.

        Args:
            serializer (object): The serializer instance for the collection data.

        Returns:
            Dict[str, str]: A dictionary containing the UUID of the newly created collection.
        """ # noqa
        serializer.is_valid(raise_exception=True)
        collection = serializer.save()
        response = {"collection_uuid": collection.uuid}
        return response


class UpdateCollectionService:

    def update_collections(self, serializer: object):
        """
        Updates a collection using the provided serializer and returns the updated data.

        Args:
            serializer (object): The serializer instance for the collection data.

        Returns:
            Dict[str, Any]: A dictionary containing the updated collection's title, description, and movies.
        """# noqa
        serializer.is_valid(raise_exception=True)
        updated_collection = serializer.save()
        movies_data = MovieSerializer(updated_collection.movies.all(),
                                      many=True).data

        return {
            "title": updated_collection.title,
            "description": updated_collection.description,
            "movies": movies_data,
        }
