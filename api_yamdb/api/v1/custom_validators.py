from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть <me>.',
            params={'value': value},
        )


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(
            f'{year}? нельзя добавлять произведения из будущего')
