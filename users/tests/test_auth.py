from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APITestCase

from users.factories import COMMON_PASSWORD, UserFactory
from users.models import User


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RegistrationAPIViewTestCase(APITestCase):
    """TestCase for RegistrationAPIView."""

    def setUp(self) -> None:
        self.url = reverse("users:registration")
        self.min_data = {
            "email": "test123@gmail.com",
            "password": "tomciopaluch5032",
            "terms_accepted": True,
        }

    def test_post_creates_user(self):
        data = self.min_data
        expected_data = {
            "email": data["email"],
            "terms_accepted": data["terms_accepted"],
        }

        response = self.client.post(self.url, data)

        self.assertJSONEqual(response.content, expected_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_post_returns_error_when_email_exists(self):
        data = self.min_data
        data["email"] = UserFactory().email
        expected_data = {"email": ["user with this email address already exists."]}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_data)

    def test_post_returns_error_when_password_is_too_weak(self):
        data = self.min_data | {
            "password": f"{self.min_data['email']}12",
        }
        expected_data = {
            "non_field_errors": ["The password is too similar to the email address."],
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_data)

    def test_post_returns_error_when_terms_not_accepted(self):
        data = self.min_data
        data["terms_accepted"] = False
        expected_data = {"terms_accepted": ["You must accept terms and conditions."]}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_data)

    def test_post_does_not_log_user_in(self):
        data = self.min_data

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertTrue("_auth_user_id" not in self.client.session)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class LoginAPIViewTestCase(APITestCase):
    """TestCase for LoginAPIView."""

    def setUp(self) -> None:
        self.url = reverse("users:login")

    def test_post_logs_user_in(self):
        password = make_password(COMMON_PASSWORD)
        user = UserFactory(password=password)
        data = {
            "email": user.email,
            "password": COMMON_PASSWORD,
        }
        expected_data = {
            "email": user.email,
            "id": str(user.pk),
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_data)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_post_returns_error_when_wrong_email(self):
        password = make_password(COMMON_PASSWORD)
        UserFactory(password=password)
        data = {
            "email": "wrongemail@yahoo.com",
            "password": COMMON_PASSWORD,
        }
        expected_data = {"non_field_errors": ["Wrong e-mail or password."]}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_data)

    def test_post_returns_error_when_wrong_password(self):
        password = make_password(COMMON_PASSWORD)
        user = UserFactory(password=password)
        data = {
            "email": user.email,
            "password": "different",
        }
        expected_data = {"non_field_errors": ["Wrong e-mail or password."]}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_data)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class LogoutAPIViewTestCase(APITestCase):
    """Tests for LogoutAPIView."""

    def setUp(self) -> None:
        self.url = reverse("users:logout")

    def test_post_logs_out_the_user(self):
        password = make_password(COMMON_PASSWORD)
        user = UserFactory(password=password)
        self.client.force_authenticate(user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse("_auth_user_id" in self.client.session)
