import uuid

from django.db import models


class Collection(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # noqa
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(default="")


class Movie(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # Use UUID as the primary key
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(default="")
    genres = models.CharField(max_length=255, default="")
    collection = models.ForeignKey(
        Collection, related_name="movies", on_delete=models.CASCADE
    )
