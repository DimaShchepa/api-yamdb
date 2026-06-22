from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from creations.models import Category, Comment, Genre, Review, Title
from users.models import User

from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (
    CategotySerializer,
    CommentSerializer,
    CurrentUserSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
    """Register a user and send a confirmation code by email."""
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
@permission_classes((AllowAny,))
def token(request):
    """Issue a JWT token in exchange for a valid confirmation code."""
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
    """Provide administrator access to user accounts."""

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
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def me(self, request):
        """Return or update the authenticated user's profile."""
        if request.method == 'GET':
            serializer = CurrentUserSerializer(request.user)
            return Response(serializer.data)

        serializer = CurrentUserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """Provide API operations for works."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Save a work using the authenticated user."""
        serializer.save(author=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """Provide API operations for reviews of a work."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_title(self):
        """Return the work specified in the URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Return reviews belonging to the selected work."""
        title = self.get_title()
        try:
            title = Title.objects.get(id=title)
            return Review.objects.filter(title=title).select_related('author')
        except Title.DoesNotExist:
            return Review.objects.none()

    def perform_create(self, serializer):
        """Save a review with its author and work."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Provide API operations for comments."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_title(self):
        """Return the work specified in the URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Return comments belonging to the selected work."""
        title = self.get_title()
        return title.comments.all()

    def perform_create(self, serializer):
        """Save a comment with its author and work."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(viewsets.ModelViewSet):
    """Provide API operations for work categories."""

    queryset = Category.objects.all()
    serializer_class = CategotySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    """Provide API operations for work genres."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
