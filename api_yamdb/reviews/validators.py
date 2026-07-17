from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


username_validator = UnicodeUsernameValidator()


def validate_year(value):
    """Reject publication years later than the current year."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год не может быть больше текущего ({current_year}).'
        )
