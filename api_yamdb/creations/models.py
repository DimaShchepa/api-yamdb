from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


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
                                 blank=False,
                                 related_name='titles')
    genre = models.ManyToManyField(
        Genre, blank=True, related_name='titles')
    name = models.CharField(max_length=256,)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.CharField(max_length=256)
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('title', 'author')


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='comments',
                              default=1)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
