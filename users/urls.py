from django.urls import path

from users.views import LoginAPIView, LogoutAPIView, RegistrationAPIView

app_name = "users"

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("registration/", RegistrationAPIView.as_view(), name="registration"),
]
