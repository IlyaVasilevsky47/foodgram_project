from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username_not_me


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Адрес электронной почты",
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username_not_me],
        verbose_name="Имя аккаунта",
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя пользователя",
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия пользователя",
    )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"],
                name="unique_name",
            ),
        ]
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
