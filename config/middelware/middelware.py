# middleware.py
from django.core.cache import caches


class RequestCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        caches_ = caches['default']
        if caches_.get('request_count') is None:
            caches_.set('request_count', 0,  timeout=None)

        caches_.incr('request_count')
        response = self.get_response(request)
        return response
