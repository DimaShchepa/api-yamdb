from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotAuthenticated

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from creations.models import Title, Review, Comment, Category, Genre

from .permissions import IsAdmin, IsAuthorModeratorAdminOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    MeSerializer, SignupSerializer,
    TokenSerializer, UserSerializer,
    TitleSerializer, CategorySerializer,
    GenreSerializer, ReviewSerializer, CommentSerializer
)


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Код подтверждения YaMDb',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=None,
        recipient_list=(user.email,),
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )
    confirmation_code = serializer.validated_data['confirmation_code']
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': 'Неверный код подтверждения.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(
        {'token': str(AccessToken.for_user(user))},
        status=status.HTTP_200_OK,
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me',
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = MeSerializer(request.user)
            return Response(serializer.data)

        serializer = MeSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category',)
    serializer_class = TitleSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def filter_queryset(self, queryset):

        category_slugs = self.request.query_params.getlist('category')
        if category_slugs:
            category_slugs = [c.strip() for c in category_slugs if c.strip()]
            if category_slugs:
                queryset = queryset.filter(category__slug__in=category_slugs)

        # # --- ФИЛЬТР ПО ЖАНРУ (по slug) ---
        genre_slugs = self.request.query_params.getlist('genre')
        if genre_slugs:
            genre_slugs = [g.strip() for g in genre_slugs if g.strip()]
            if genre_slugs:
                queryset = queryset.filter(genre__slug__in=genre_slugs).distinct()

        year_param = self.request.query_params.get('year')
        if year_param:
            try:
                year_value = int(year_param)
                queryset = queryset.filter(year=year_value)
            except (ValueError, TypeError):
                pass

        name_param = self.request.query_params.get('name')
        if name_param:
            queryset = queryset.filter(name__icontains=name_param)

        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        if not title_id:
            raise ValidationError({'title_id': 'Требуется ID произвеления'})
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        title = self.get_title()
        return Review.objects.filter(title=title).select_related('author')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = self.get_title()
        return context

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    # def perform_update(self, serializer):
    #     review = serializer.instance
    #     user = self.request.user

    #     is_author = (review.author == user)
    #     is_admin = user.is_staff
    #     is_moderator = False

    #     if hasattr(user, 'role'):
    #         is_moderator = (user.role == 'moderator')

    #     if is_author or is_admin or is_moderator:
    #         serializer.save()
    #     else:
    #         raise PermissionDenied('Нет прав на редактирование отзыва')


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review,
                                 id=review_id)

    def get_queryset(self):
        review = self.get_review()
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in 'list':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)

    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
