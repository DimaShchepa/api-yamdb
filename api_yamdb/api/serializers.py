from rest_framework import serializers
from django.db.models import Avg

from users.models import User
from reviews.models import Title, Review, Comment, Category, Genre
from .validators import validate_username


class SignupSerializer(serializers.ModelSerializer):

    """Validate data used for user registration."""
    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username')
        validators = ()

    def validate(self, attrs):

        """Allow repeated signup only for the same username and email."""
        username = attrs['username']
        email = attrs['email']
        username_owner = User.objects.filter(username=username).first()
        email_owner = User.objects.filter(email=email).first()

        if username_owner and username_owner.email != email:
            raise serializers.ValidationError(
                {'username': 'Это имя пользователя уже занято.'}
            )
        if email_owner and email_owner.username != username:
            raise serializers.ValidationError(
                {'email': 'Этот адрес электронной почты уже занят.'}
            )
        return attrs

    def create(self, validated_data):
        """Create a user or return one registered with the same data."""

        user, created = User.objects.get_or_create(**validated_data)
        if created:
            user.set_unusable_password()
            user.save()
        return user


class TokenSerializer(serializers.Serializer):
    """Validate data required to obtain a JWT token."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Serialize user data for administrator endpoints."""

    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
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
        required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Title
        fields = ('id', 'category', 'genre',
                  'name', 'year', 'description')


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

    # def create(self, validated_data):
    #     user = self.context.get('request').user
    #     title = self.context.get('title')

    #     if user and title:
    #         if Review.objects.filter(title=title, author=user).exists():
    #             raise serializers.ValidationError(
    #                 {
    #                     'non_field_errors': [
    #                         'Вы уже оставили отзыв на это произведение'
    #                     ]
    #                 }
    #             )

    #     return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments on reviews."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
