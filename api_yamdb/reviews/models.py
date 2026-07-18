from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from .validators import validate_year


MAX_LENGHT = 256
MIN_SCORE = 1
MAX_SCORE = 10
PREVIEW_TEXT = 40


class Category(models.Model):
    """A model with categories"""

    name = models.CharField(max_length=MAX_LENGHT, verbose_name='Категория')
    slug = models.SlugField(unique=True)

    class Meta():
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """A model with genres"""

    name = models.CharField(max_length=MAX_LENGHT,
                            verbose_name='Название жанра')
    slug = models.SlugField(unique=True)

    class Meta():
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """A model describing the work of titles"""

    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='titles')
    genre = models.ManyToManyField(
        Genre, blank=True, related_name='titles')
    name = models.CharField(max_length=MAX_LENGHT, verbose_name='Название')
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=(validate_year,),
    )
    description = models.TextField(blank=True,)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        suffix = f' ({self.year})' if self.year else ''
        return f'{self.name}{suffix}'


class Review(models.Model):
    """A model describing the work of reviewers"""

    text = models.TextField(verbose_name='Текст отзыва')
    score = models.IntegerField(verbose_name='Оценка',
                                validators=[MinValueValidator(MIN_SCORE),
                                            MaxValueValidator(MAX_SCORE)])
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор отзыва')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [UniqueConstraint(
            fields=['title', 'author'],
            name='unique_review_per_title_and_author')]

    def __str__(self):
        return f'Отзыв {self.id} на "{self.title}" от {self.author.username}'


class Comment(models.Model):
    """A model describing how comments work"""

    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        preview = self.text[:PREVIEW_TEXT]
        if len(self.text) > PREVIEW_TEXT:
            preview += '...'
        return f'Комментарий {self.id}: {preview} от {self.author.username}'
