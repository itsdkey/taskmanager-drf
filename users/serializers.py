from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    terms_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ["email", "password", "terms_accepted"]

    def validate_terms_accepted(self, terms_accepted: bool) -> bool:
        if not terms_accepted:
            raise ValidationError(_("You must accept terms and conditions."))
        return terms_accepted

    def validate(self, attrs: dict) -> dict:
        self._validate_passwords(attrs)
        return attrs

    def _validate_passwords(self, attrs: dict) -> None:
        password = attrs["password"]
        email = attrs["email"]
        try:
            password_validation.validate_password(password, User(email=email))
        except DjangoValidationError as ex:
            raise ValidationError(ex.messages)


class LoginSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "incorrect_authentication": _("Wrong e-mail or password."),
    }

    email = serializers.EmailField()
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["email", "id", "password"]

    def validate(self, attrs: dict) -> dict:
        user: User = authenticate(
            self.context["request"],
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise ValidationError(
                self.error_messages["incorrect_authentication"],
                code="authorization",
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        return User.objects.get(email=validated_data["email"])
