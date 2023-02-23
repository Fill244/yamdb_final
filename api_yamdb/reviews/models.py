from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.v1.custom_validators import validate_year


class Category(models.Model):
    """
    Категории (типы) произведений, как («Фильмы», «Книги», «Музыка»).
    Каждое произведение относится к одной категории.
    Суперюзер и администратор могут добавлять категории.
    поля - id, name, slug
    """
    name = models.CharField(max_length=100,
                            verbose_name='название категории', unique=True)
    slug = models.SlugField(verbose_name='url', unique=True)

    class Meta:
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Жанры произведений, как Рок, Поп, Комедия... Одно произведение может
     быть привязано к нескольким жанрам.
    поля - id, name, slug
    """
    name = models.CharField(max_length=100,
                            verbose_name='название жанра', unique=True)
    slug = models.SlugField(verbose_name='url', unique=True)

    class Meta:
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Произведения, к которым пишут отзывы, каждое привязано к одной категории.
    поля - id,name,year,category
    """
    name = models.CharField(max_length=250,
                            verbose_name='название произведения')
    year = models.IntegerField(verbose_name='год выпуска произведения',
                               validators=(validate_year,))
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles',
        verbose_name='категория')
    genre = models.ManyToManyField(Genre,
                                   through='GenreTitle', verbose_name='Жанр')
    description = models.TextField(verbose_name='описание произведения',
                                   blank=True)

    class Meta:
        verbose_name_plural = 'произведения которые обсуждают пользователи'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    отзывы к шедеврам, каждый отзыв привязан к своему произведению
    поля - id, title_id, text, author, score, pub_date
    """
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='review',
        verbose_name='произведение',
        help_text='произведение к которому этот отзыв')
    text = models.TextField(verbose_name='текст отзыва')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='review', verbose_name='автор отзыва')
    score = models.IntegerField(
        verbose_name='оценка произведения',
        validators=(MaxValueValidator(10, 'оценка не может быть больше 10'),
                    MinValueValidator(0, 'оценка не может быть меньше 0'),))
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='дата добавления отзыва')

    class Meta:
        verbose_name_plural = 'отзывы и оценки к произведениям'
        constraints = (models.UniqueConstraint(fields=('author', 'title'),
                                               name='unique-review'),)

    def __str__(self):
        return self.text[:12]


class Comment(models.Model):
    """
    комментарии к отзывам, коммент привязан к своему отзыву
    поля - id, review_id, text, author, pub_date
    """
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='для какого отзыва коммент')
    text = models.TextField(verbose_name='текст комментария')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='comments', verbose_name='автор комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='дата добавления комментария')

    class Meta:
        verbose_name_plural = 'комментарии к отзывам'

    def __str__(self):
        return self.text[:12]


class GenreTitle(models.Model):
    """
    К каким жанрам относится произведение, их может быть несколько,
     как лирическая комедия.
    поля - id, title_id, genre_id
    """
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='произведение',
        related_name='genre_title')
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, verbose_name='жанр',
        related_name='genre_title')

    class Meta:
        verbose_name_plural = 'произведения и жанры, промежуточная таблица'
