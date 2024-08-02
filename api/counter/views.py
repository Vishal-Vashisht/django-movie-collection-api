from django.core.cache import caches
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

cache_ = caches['default']


class RequestCountAPIView(APIView):
    """
    API view to return the total number of requests served.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request) -> Response:

        """return the total number of requests served"""
        try:
            request_count = cache_.get('request_count', 0)
            return Response({"requests": request_count},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetRequestCountAPIView(APIView):
    """
    API view to reset the request count.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request) -> Response:

        """ Reset the request count"""
        try:
            cache_.set('request_count', 0)
            return Response({"message": "Request count reset successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
