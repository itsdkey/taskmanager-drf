from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

from users.querysets import UserQuerySet


class UserManager(DjangoUserManager.from_queryset(UserQuerySet), DjangoUserManager):
    """An overwritten Manager.

    When creating a superuser there were some issues because of a custom
    USERNAME_FIELD.
    """

    def _create_user(
        self,
        username: str = None,
        email: str = None,
        password: str = None,
        **extra_fields
    ):
        """Creates and saves a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str = None,
        email: str = None,
        password: str = None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, email, password, **extra_fields)

    def create_superuser(
        self,
        username: str = None,
        email: str = None,
        password: str = None,
        **extra_fields
    ):
        """Creates and saves a superuser with the given email and password."""
        return super().create_superuser(
            email, email=email, password=password, **extra_fields
        )
