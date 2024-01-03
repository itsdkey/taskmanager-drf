from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractUser):
    """A custom model representing our User."""

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    username = None
    email = models.EmailField(verbose_name=_("email address"), unique=True)

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid4,
        editable=False,
    )

    terms_accepted = models.BooleanField(
        verbose_name=_("Terms and conditions"),
        help_text=_("True if terms and conditions were accepted."),
        default=False,
    )

    objects = UserManager()
