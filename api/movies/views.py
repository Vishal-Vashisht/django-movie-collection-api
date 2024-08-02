import requests
from django.db import IntegrityError, transaction
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .constants.error_messages import GENERAL_ERRORS
from .constants.logger import logger
from .models import Collection
from .serializers import CollectionSerializer
from .services import (CreateCollectionService, ListCollectionsService,
                       MovieListService, UpdateCollectionService)


class MovieListView(generics.ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    movie_list_service = MovieListService()

    def get(self, request, *args, **kwargs):

        try:
            data = self.movie_list_service.get_list(request)
            return Response(data, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as http_err:
            logger.exception(str(http_err))
            return Response(
                {"error": str(http_err)}, status=http_err.response.status_code
            )
        except requests.RequestException as requestexp:
            logger.exception(str(requestexp))
            return Response(
                {"error": str(requestexp)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response(
                GENERAL_ERRORS["INTERNAL_SERVER_ERROR"],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CollectionViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    list_collection_service = ListCollectionsService()
    create_collection_service = CreateCollectionService()
    update_collection_service = UpdateCollectionService()

    def list(self, request) -> Response:
        """
        Retrieves a list of collections and returns them in the response.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A Response object containing the collections or an error message.
        """ # noqa
        try:
            response = self.list_collection_service.get_collections(
                self.queryset
            )
            return Response(
                response, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)})

    @transaction.atomic
    def create(self, request) -> Response:
        """
        Creates a new collection based on the provided request data.

        Args:
            request: The HTTP request object containing collection data.

        Returns:
            Response: A Response object containing the created collection's UUID or an error message.
        """ # noqa
        try:

            serializer = self.get_serializer(data=request.data)
            response = self.create_collection_service.create_collection(
                serializer)
            return Response(
                response,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            logger.exception(str(e))
            return Response({"error": e.detail},
                            status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.exception(str(e))
            return Response(
                GENERAL_ERRORS["INTEGRITY_ERROR"],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.exception(str(e))
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def update(self, request, pk=None) -> Response:
        """
        Updates an existing collection based on the provided request data.

        Args:
            request: The HTTP request object containing updated collection data.
            pk (int, optional): The primary key of the collection to update.

        Returns:
            Response: A Response object containing the updated collection's data or an error message.
        """ # noqa
        try:
            collection = self.get_object()
            serializer = self.get_serializer(
                collection, data=request.data, partial=False)

            response = self.update_collection_service.update_collections(
                serializer
            )

            return Response(
                response, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            logger.exception(str(e))
            return Response({"error": e.detail},
                            status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.exception(str(e))
            return Response(
                GENERAL_ERRORS["INTEGRITY_ERROR"],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.exception(str(e))
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
