from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256,)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Title(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='titles')
    genre = models.ForeignKey(Genre,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              related_name='titles')
    name = models.CharField(max_length=256,)
    year = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(timezone.now().year)
        ]
    )
    description = models.TextField()
    rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.CharField(max_length=256)
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)


class Comment(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.CharField()
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
