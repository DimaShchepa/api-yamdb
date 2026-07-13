from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers


username_validator = UnicodeUsernameValidator()


def validate_username(value):
    if value == 'me':
        raise serializers.ValidationError(
            'Использовать "me" в качестве username запрещено.'
        )
    username_validator(value)
    return value
