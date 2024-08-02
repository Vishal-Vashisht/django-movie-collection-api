from rest_framework import serializers
from .models import Collection, Movie


class MovieSerializer(serializers.ModelSerializer):

    genres = serializers.CharField(allow_blank=True)
    uuid = serializers.UUIDField(required=True)

    class Meta:
        model = Movie
        fields = ["uuid", "title", "description", "genres"]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CollectionSerializer(serializers.ModelSerializer):

    movies = MovieSerializer(many=True)

    class Meta:
        model = Collection
        fields = ["uuid", "title", "description", "movies"]

    def create(self, validated_data):
        movies_data = validated_data.pop("movies")
        collection = Collection.objects.create(**validated_data)
        for movie_data in movies_data:
            Movie.objects.create(collection=collection, **movie_data)
        return collection

    def update(self, instance, validated_data):
        movies_data = validated_data.pop("movies", [])
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get(
            "description", instance.description)
        instance.save()

        for movies in movies_data:
            movie_ins = instance.movies.get(uuid=movies["uuid"])
            if movie_ins:
                MovieSerializer().update(movie_ins, movies)

        return instance
