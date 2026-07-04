from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Store YaMDb user profile and role."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        """Return whether the user has administrator rights."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Return whether the user has the moderator role."""
        return self.role == self.MODERATOR
