from rest_framework import viewsets

from creations.models import User, Title, Review, Comment, Category, Genre
from .serializers import TitleSerializer, CategotySerializer, GenreSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategotySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer