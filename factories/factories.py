import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from api.movies.models import Movie, Collection
import uuid


class UserFactory(factory.django.DjangoModelFactory):

    """Factory for creating User instances for testing."""
    class Meta:
        model = User

    username = factory.Faker('user_name')  # Generates a random username
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class CollectionFactory(DjangoModelFactory):
    """Factory for creating Collection instances for testing."""
    class Meta:
        model = Collection

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text')


class MovieFactory(DjangoModelFactory):
    """Factory for creating Movie instances for testing."""
    class Meta:
        model = Movie

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text')
    genres = factory.Faker('word')
    uuid = factory.LazyFunction(uuid.uuid4)
    collection = factory.SubFactory(CollectionFactory)
