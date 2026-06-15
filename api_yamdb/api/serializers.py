from rest_framework import serializers

from users.models import User
from creations.models import Title, Review, Comment, Category, Genre
from .validators import validate_username


class SignupSerializer(serializers.ModelSerializer):
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
        user, created = User.objects.get_or_create(**validated_data)
        if created:
            user.set_unusable_password()
            user.save(update_fields=('password',))
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
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
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                'Это имя пользователя уже занято.'
            )
        return value


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    # genre = GenreSerializer(many=True)
    # category_slug = serializers.SlugRelatedField(
    #     queryset=Category.objects.all(),
    #     write_only=True,
    #     slug_field='slug',
    #     required=False
    # )
    # genre_slugs = serializers.SlugRelatedField(
    #     queryset=Genre.objects.all(),
    #     write_only=True,
    #     slug_field='slug',
    #     many=True,
    #     required=False
    # )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Title
        fields = ('id', 'category', 'genre',
                  'name', 'year', 'description')
        read_only_fields = ('description',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'title', 'pub_date', 'author')
        read_only_fields = ('pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'review', 'pub_date', 'title')
