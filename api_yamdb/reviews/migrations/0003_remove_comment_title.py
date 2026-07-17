from django.db import migrations
from django.db import models

import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_review_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={
                'ordering': ('name',),
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={
                'ordering': ('pub_date',),
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
            },
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={
                'ordering': ('name',),
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.AlterModelOptions(
            name='review',
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.AlterModelOptions(
            name='title',
            options={
                'ordering': ('-year', 'name'),
                'verbose_name': 'Произведение',
                'verbose_name_plural': 'Произведения',
            },
        ),
        migrations.RemoveField(
            model_name='comment',
            name='title',
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(
                validators=(reviews.validators.validate_year,),
                verbose_name='Год выпуска',
            ),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
