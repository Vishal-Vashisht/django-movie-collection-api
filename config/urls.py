"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from api.counter.views import RequestCountAPIView, ResetRequestCountAPIView
from api.movies.views import CollectionViewSet, MovieListView
from api.user_auth.views import RegisterView
from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"collections", CollectionViewSet, basename='collection')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", RegisterView.as_view(), name="register"),
    path("movies/", MovieListView.as_view(), name="movies"),
    path('request-count/', RequestCountAPIView.as_view(), name='request-count'),# noqa
    path('request-count/reset/', ResetRequestCountAPIView.as_view(), name='reset-request-count'), # noqa
]

urlpatterns += router.urls
