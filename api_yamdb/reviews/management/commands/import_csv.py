import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_datetime

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class Command(BaseCommand):
    """Import YaMDb data from CSV files."""

    help = 'Импортирует данные YaMDb из CSV-файлов.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=Path,
            default=Path(settings.BASE_DIR) / 'static' / 'data',
            help='Каталог с CSV-файлами.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = options['data_dir'].resolve()
        if not data_dir.is_dir():
            raise CommandError(f'Каталог с данными не найден: {data_dir}')

        importers = (
            ('users.csv', self._import_user),
            ('category.csv', self._import_category),
            ('genre.csv', self._import_genre),
            ('titles.csv', self._import_title),
            ('genre_title.csv', self._import_genre_title),
            ('review.csv', self._import_review),
            ('comments.csv', self._import_comment),
        )
        imported = {}

        for filename, importer in importers:
            imported[filename] = self._import_file(
                data_dir / filename,
                importer,
            )

        total = sum(imported.values())
        details = ', '.join(
            f'{filename}: {count}'
            for filename, count in imported.items()
        )
        self.stdout.write(self.style.SUCCESS(
            f'Импорт завершён: {total} записей ({details}).'
        ))

    def _import_file(self, path, importer):
        if not path.is_file():
            raise CommandError(f'CSV-файл не найден: {path}')

        with path.open(encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise CommandError(f'В CSV-файле нет заголовка: {path}')

            count = 0
            for row_number, row in enumerate(reader, start=2):
                try:
                    importer(row, path.name, row_number)
                except (
                    IntegrityError, KeyError, TypeError, ValueError
                ) as exc:
                    raise CommandError(
                        f'Ошибка в файле {path.name}, строка {row_number}: '
                        f'{exc}'
                    ) from exc
                count += 1
        return count

    @staticmethod
    def _import_user(row, filename, row_number):
        user, created = User.objects.update_or_create(
            id=int(row['id']),
            defaults={
                'username': row['username'],
                'email': row['email'],
                'role': row['role'],
                'bio': row.get('bio', ''),
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=('password',))

    @staticmethod
    def _import_category(row, filename, row_number):
        Category.objects.update_or_create(
            id=int(row['id']),
            defaults={'name': row['name'], 'slug': row['slug']},
        )

    @staticmethod
    def _import_genre(row, filename, row_number):
        Genre.objects.update_or_create(
            id=int(row['id']),
            defaults={'name': row['name'], 'slug': row['slug']},
        )

    @staticmethod
    def _import_title(row, filename, row_number):
        category = row.get('category')
        Title.objects.update_or_create(
            id=int(row['id']),
            defaults={
                'name': row['name'],
                'year': int(row['year']),
                'category_id': int(category) if category else None,
                'description': row.get('description', ''),
            },
        )

    @staticmethod
    def _import_genre_title(row, filename, row_number):
        Title.genre.through.objects.update_or_create(
            id=int(row['id']),
            defaults={
                'title_id': int(row['title_id']),
                'genre_id': int(row['genre_id']),
            },
        )

    @staticmethod
    def _import_review(row, filename, row_number):
        pub_date = Command._parse_datetime(
            row['pub_date'], filename, row_number
        )
        review, _ = Review.objects.update_or_create(
            id=int(row['id']),
            defaults={
                'title_id': int(row['title_id']),
                'text': row['text'],
                'author_id': int(row['author']),
                'score': int(row['score']),
                'pub_date': pub_date,
            },
        )
        Review.objects.filter(pk=review.pk).update(pub_date=pub_date)

    @staticmethod
    def _import_comment(row, filename, row_number):
        pub_date = Command._parse_datetime(
            row['pub_date'], filename, row_number
        )
        comment, _ = Comment.objects.update_or_create(
            id=int(row['id']),
            defaults={
                'review_id': int(row['review_id']),
                'text': row['text'],
                'author_id': int(row['author']),
                'pub_date': pub_date,
            },
        )
        Comment.objects.filter(pk=comment.pk).update(pub_date=pub_date)

    @staticmethod
    def _parse_datetime(value, filename, row_number):
        parsed = parse_datetime(value)
        if parsed is None:
            raise ValueError(
                f'некорректная дата в {filename}, строка {row_number}: '
                f'{value}'
            )
        return parsed
