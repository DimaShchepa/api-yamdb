from django.utils import timezone
from rest_framework import serializers
from django.db.models import Avg

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
            user.save()
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


class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):

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
                  'name', 'year', 'description', 'rating')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['rating'] = self.get_rating(instance)
        if instance.category:
            data['category'] = CategorySerializer(instance.category).data
        data['genre'] = [
            {'name': genre.name, 'slug': genre.slug}
            for genre in instance.genre.all()
        ]
        return data

    def validate_year(self, value):
        current_year = timezone.now().year
        if value < 1 or value > current_year:
            raise serializers.ValidationError(
                f"Год должен быть между 1 и {current_year}."
            )
        return value

    def get_rating(self, obj):
        reviews = getattr(obj, 'reviews', None)
        if not reviews:
            return None
        result = reviews.aggregate(avg_score=Avg('score'))['avg_score']
        return round(result) if result is not None else None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'title', 'pub_date', 'author')
        read_only_fields = ('pub_date', 'title')

    def create(self, validated_data):
        user = self.context.get('request').user
        title = self.context.get('title')

        if user and title:
            if Review.objects.filter(title=title, author=user).exists():
                raise serializers.ValidationError(
                    {
                        'non_field_errors': [
                            'Вы уже оставили отзыв на это произведение'
                        ]
                    }
                )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
        read_only_fields = ('pub_date',)
