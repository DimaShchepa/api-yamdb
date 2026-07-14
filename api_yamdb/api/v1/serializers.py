from django.db.models import Avg
from rest_framework import serializers

from users.models import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH, User
from users.validators import (
    unicode_username_validator, validate_reserved_username
)
from reviews.models import Title, Review, Comment, Category, Genre


class SignupSerializer(serializers.Serializer):

    """Validate data used for user registration."""
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(validate_reserved_username, unicode_username_validator),
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    def validate(self, attrs):
        """Allow repeated signup only for the same username and email."""
        username = attrs['username']
        email = attrs['email']
        username_owner = User.objects.filter(username=username).first()
        email_owner = User.objects.filter(email=email).first()
        errors = {}

        if username_owner and username_owner.email != email:
            errors['username'] = 'Это имя пользователя уже занято.'
        if email_owner and email_owner.username != username:
            errors['email'] = 'Этот адрес электронной почты уже занят.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TokenSerializer(serializers.Serializer):
    """Validate data required to obtain a JWT token."""

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Serialize user data for administrator endpoints."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(validate_reserved_username, unicode_username_validator),
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        """Check that username is not used by another user."""
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                'Это имя пользователя уже занято.'
            )
        return value


class CurrentUserSerializer(UserSerializer):
    """Serialize the current user without allowing role changes."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Serialize work categories."""

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):
    """Serialize work genres."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Serialize works and their category and genres."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = ('id', 'category', 'genre',
                  'name', 'year', 'description')

    def to_representation(self, instance):
        """Return a title using the response schema from the API docs."""
        instance.rating = instance.reviews.aggregate(
            rating=Avg('score')
        )['rating']
        return TitleReadSerializer(instance, context=self.context).data


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.ReadOnlyField()

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'description',
                  'category', 'genre', 'rating']


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize user reviews."""

    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'pub_date', 'author')

    def validate(self, attrs):
        if self.instance is not None:
            return attrs

        request = self.context.get('request')
        title = self.context.get('title')

        if not request or not title:
            raise serializers.ValidationError(
                'Не хватает контекста: request или title')

        user = request.user

        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                {'non_field_errors':
                 ['Вы уже оставили отзыв на это произведение']}
            )

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments on reviews."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
