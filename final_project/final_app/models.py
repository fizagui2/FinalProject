from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """The project's user account.

    Subclasses AbstractUser so we keep Django's password hashing, sessions
    and permissions while still being able to add GameHub fields later.
    Swapping AUTH_USER_MODEL after the first migration is applied is very
    painful, which is why this exists up front even though it is nearly empty.
    """

    display_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    """A gaming category that news articles and forum posts belong to."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
