from typing import Dict, Union

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.forms import EmailField

User = get_user_model()


def email_body(user: User) -> Dict[str, Union[str, EmailField]]:
    """Подготовка текста сообщения для регистрации."""
    message = (f'Здравствуйте {user.username}.'
               ' Код подтвержения для доступа к API:'
               f' {user.confirmation_code}')
    data = {
        'email_body': message,
        'to_email': user.email,
        'email_subject': 'Код подтвержения для доступа к API!'
    }
    return data


def send_email(user: User) -> None:
    """Отправка сообщения с кодом подтверждения регистрации."""
    data = email_body(user)
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=(data['to_email'],)
    )
    email.send()
