from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from users.serializers import LoginSerializer, RegistrationSerializer


@extend_schema_view(
    post=extend_schema(
        description="Logout a User.",
        responses={status.HTTP_204_NO_CONTENT: None},
    ),
)
class LogoutAPIView(APIView):
    """Log out a User."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        logout(self.request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    post=extend_schema(
        description="Log in a User via email and password.",
        responses={status.HTTP_200_OK: LoginSerializer},
    ),
)
class LoginAPIView(APIView):
    """Log in a User."""

    serializer_class = LoginSerializer
    parser_classes = api_settings.DEFAULT_PARSER_CLASSES

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        description="Create a User account with given credentials.",
        responses={status.HTTP_201_CREATED: RegistrationSerializer},
    ),
)
class RegistrationAPIView(CreateAPIView):
    """Register a new Vendor User."""

    serializer_class = RegistrationSerializer
