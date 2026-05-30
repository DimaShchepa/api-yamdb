from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Categories(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)


class Genres(models.Model):
    name = models.CharField(max_length=256,)
    slug = models.SlugField(unique=True, max_length=50)


class Titles(models.Model):
    category = models.ForeignKey(Categories,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='titles')
    genre = models.ForeignKey(Genres,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              related_name='titles')
    name = models.CharField(max_length=256,)
    year = models.IntegerField()
    description = models.TextField(max_length=256)
    rating = models.IntegerField(null=True, blank=True)


class Reviews(models.Model):
    text = models.CharField(max_length=256)
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    title = models.ForeignKey(Titles, on_delete=models.CASCADE,
                              related_name='reviews')
