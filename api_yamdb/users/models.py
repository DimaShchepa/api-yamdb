from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import unicode_username_validator, validate_reserved_username


USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
ROLE_MAX_LENGTH = 20


class User(AbstractUser):
    """Store YaMDb user profile and role."""

    class Role(models.TextChoices):
        USER = 'user', 'User'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(validate_reserved_username, unicode_username_validator),
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        """Return whether the user has administrator rights."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Return whether the user has the moderator role."""
        return self.role == self.Role.MODERATOR
