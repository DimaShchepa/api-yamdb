from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


FORBIDDEN_USERNAMES = ('me',)

unicode_username_validator = UnicodeUsernameValidator()


def validate_reserved_username(value):
    """Check that username is not reserved by the API."""
    if value in FORBIDDEN_USERNAMES:
        raise ValidationError(
            'Использовать "me" в качестве username запрещено.'
        )
    return value
