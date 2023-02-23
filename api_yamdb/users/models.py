from django.contrib.auth.models import AbstractUser
from django.db import models

from api.v1.custom_validators import validate_username

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = (
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
)


class User(AbstractUser):
    """
    Расширенная модель Users, нам нужны такие поля:
     id, username, email, role, bio, first_name, last_name
    К пользователю могут быть привязаны комментарии, отзывы
    role: admin, moderator, user
    """
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(verbose_name='биография', blank=True)
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        default='ussr'
    )
    username = models.CharField(
        'username',
        validators=(validate_username,),
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        'email',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
