from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.core.exceptions import ValidationError


unicode_username_validator = UnicodeUsernameValidator()


def validate_reserved_username(value):
    """Check that username is not reserved by the API."""
    if value in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Использовать "{value}" в качестве username запрещено.'
        )
    return value
