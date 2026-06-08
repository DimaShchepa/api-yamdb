from rest_framework import serializers

from creations.models import User, Title, Review, Comment, Category, Genre


class CategotySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Mata:
        model = Genre
        fields = ('slug', 'name')


class TitleSerializer(serializers.ModelSerializer):
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
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'title', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
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
