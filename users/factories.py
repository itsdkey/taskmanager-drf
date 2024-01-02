import factory

from users.models import User

COMMON_PASSWORD = "Passw0rdForTest1ing"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    is_active = True
    is_staff = False
    email = factory.Faker("email")

    terms_accepted = True
