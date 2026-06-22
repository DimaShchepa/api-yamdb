from rest_framework import serializers

from creations.models import Category, Comment, Genre, Review, Title
from users.models import User

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
            user.save(update_fields=('password',))
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


class CategotySerializer(serializers.ModelSerializer):
    """Serialize work categories."""

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):
    """Serialize work genres."""

    class Mata:
        model = Genre
        fields = ('slug', 'name')


class TitleSerializer(serializers.ModelSerializer):
    """Serialize works and their category and genres."""

    genre = GenreSerializer(many=True)
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        slug_field='slug',
        required=False
    )
    genre_slugs = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        write_only=True,
        slug_field='slug',
        many=True,
        required=False
    )

    class Meta:
        model = Title
        fields = ('id', 'category', 'category_slug', 'genre', 'genre_slug',
                  'name', 'year', 'description')
        read_only_fields = ('genre', 'description', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize user reviews."""

    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'title', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments on reviews."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    # review = serializers.SlugRelatedField(
    #     queryset=Review.objects.all(),
    #     slug_field='slug',
    #     read_only=True,
    # )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'review', 'pud_date', 'title')
