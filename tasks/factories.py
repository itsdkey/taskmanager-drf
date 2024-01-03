import factory
from factory.fuzzy import FuzzyChoice

from tasks.models import Task, TaskState


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    owner = factory.SubFactory("users.factories.UserFactory")
    title = factory.Faker("text", max_nb_chars=10)
    description = factory.Faker("paragraph", nb_sentences=5)
    state = FuzzyChoice(TaskState.values)
    due_date = factory.Faker("future_date")
