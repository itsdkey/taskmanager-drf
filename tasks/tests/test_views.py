from datetime import timedelta
from unittest.mock import ANY

from django.utils.timezone import now
from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from tasks.factories import TaskFactory
from tasks.models import Task, TaskState
from users.factories import UserFactory


class TaskViewSetTestCase(APITestCase):
    """TestCase for TaskViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

    def setUp(self) -> None:
        self.url = reverse("tasks:task-list")

    @staticmethod
    def _prepare_task_response(task: Task) -> dict:
        return {
            "description": task.description,
            "due_date": task.due_date.isoformat(),
            "id": str(task.pk),
            "state": str(task.state),
            "title": task.title,
        }

    def test_list_returns_forbidden_for_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_list_queries_count(self):
        self.client.force_authenticate(self.user)
        expected_queries = 1

        with self.assertNumQueries(expected_queries):
            self.client.get(self.url)

    def test_list_returns_users_upcoming_tasks(self):
        self.client.force_authenticate(self.user)
        today = now()
        dates = [
            (today - timedelta(days=1)).date(),
            today.date(),
            (today + timedelta(days=1)).date(),
        ]
        TaskFactory.create_batch(size=3)
        tasks = TaskFactory.create_batch(
            size=len(dates),
            due_date=Iterator(dates),
            owner=self.user,
        )
        expected_data = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [self._prepare_task_response(t) for t in tasks[1:]],
        }

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_data)

    def test_list_filters_tasks_by_upcoming_date(self):
        self.client.force_authenticate(self.user)
        today = now()
        dates = [
            (today - timedelta(days=1)).date(),
            today.date(),
            (today + timedelta(days=1)).date(),
        ]
        tasks = TaskFactory.create_batch(
            size=len(dates),
            due_date=Iterator(dates),
            owner=self.user,
        )
        params = {"due_date": dates[2]}
        expected_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [self._prepare_task_response(tasks[2])],
        }

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_data)

    def test_retrieve_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_retrieve_queries_count(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user)
        url = reverse("tasks:task-detail", args=[task.pk])
        expected_queries = 1

        with self.assertNumQueries(expected_queries):
            self.client.get(url)

    def test_retrieve_returns_task_for_its_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user)
        url = reverse("tasks:task-detail", args=[task.pk])
        expected_response = self._prepare_task_response(task)

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_response)

    def test_create_returns_forbidden_for_anonymous_user(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create_creates_task_for_user(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory.build(owner=self.user, state=TaskState.TO_DO)
        data = {
            "due_date": task.due_date,
            "title": task.title,
            "description": task.description,
        }
        expected_response = self._prepare_task_response(task)
        expected_response |= {"id": ANY}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertJSONEqual(response.content, expected_response)

    def test_create_returns_error_when_date_is_in_the_past(self):
        self.client.force_authenticate(self.user)
        data = {
            "due_date": (now() - timedelta(days=1)).date(),
            "title": "Task title",
            "description": "Task description",
            "state": TaskState.TO_DO,
        }
        expected_response = {
            "due_date": ["This date cannot be in the past."],
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)

    def test_update_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.put(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_update_updates_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.IN_PROGRESS)
        url = reverse("tasks:task-detail", args=[task.pk])
        data = {
            "due_date": (now() + timedelta(days=1)).date(),
            "title": "New Task title",
            "description": "New Task description",
        }
        expected_response = self._prepare_task_response(task)
        expected_response |= data
        expected_response["due_date"] = expected_response["due_date"].isoformat()

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_response)

    def test_update_returns_error_when_due_date_in_the_past(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.IN_PROGRESS)
        url = reverse("tasks:task-detail", args=[task.pk])
        data = {
            "due_date": (now() - timedelta(days=1)).date(),
            "title": "New Task title",
            "description": "New Task description",
        }
        expected_response = {
            "due_date": ["This date cannot be in the past."],
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)

    def test_partial_update_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.patch(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_partial_update_updates_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.IN_PROGRESS)
        url = reverse("tasks:task-detail", args=[task.pk])
        data = {
            "due_date": (now() + timedelta(days=1)).date(),
        }
        expected_response = self._prepare_task_response(task)
        expected_response |= {"due_date": data["due_date"].isoformat()}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_response)

    def test_partial_update_returns_error_when_due_date_in_the_past(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.IN_PROGRESS)
        url = reverse("tasks:task-detail", args=[task.pk])
        data = {
            "due_date": (now() - timedelta(days=1)).date(),
        }
        expected_response = {
            "due_date": ["This date cannot be in the past."],
        }
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)

    def test_delete_update_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_deletes_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user)
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_mark_to_do_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-mark-to-do", args=[task.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_mark_to_do_returns_updated_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.IN_PROGRESS)
        url = reverse("tasks:task-mark-to-do", args=[task.pk])
        expected_response = self._prepare_task_response(task)
        expected_response |= {"state": TaskState.TO_DO}

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_response)

    def test_mark_to_do_returns_returns_error_when_task_is_done(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.DONE)
        url = reverse("tasks:task-mark-to-do", args=[task.pk])
        expected_response = {
            "state": ["This task is already done."],
        }

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)

    def test_mark_in_progress_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-mark-in-progress", args=[task.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_mark_in_progress_returns_updated_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.TO_DO)
        url = reverse("tasks:task-mark-in-progress", args=[task.pk])
        expected_response = self._prepare_task_response(task)
        expected_response |= {"state": TaskState.IN_PROGRESS}

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content, expected_response)

    def test_mark_in_progress_returns_returns_error_when_task_is_done(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.DONE)
        url = reverse("tasks:task-mark-in-progress", args=[task.pk])
        expected_response = {
            "state": ["This task is already done."],
        }

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)

    def test_mark_done_returns_forbidden_for_anonymous_user(self):
        task = TaskFactory()
        url = reverse("tasks:task-detail", args=[task.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_mark_done_returns_updated_task_when_user_is_owner(self):
        self.client.force_authenticate(self.user)
        tasks = TaskFactory.create_batch(
            size=2,
            owner=self.user,
            state=Iterator([TaskState.TO_DO, TaskState.IN_PROGRESS]),
        )
        for task in tasks:
            with self.subTest(taskstate=task.state):
                url = reverse("tasks:task-mark-done", args=[task.pk])
                expected_response = self._prepare_task_response(task)
                expected_response |= {"state": TaskState.DONE}

                response = self.client.post(url)

                self.assertEqual(response.status_code, HTTP_200_OK)
                self.assertJSONEqual(response.content, expected_response)

    def test_mark_done_returns_returns_error_when_task_is_done(self):
        self.client.force_authenticate(self.user)
        task = TaskFactory(owner=self.user, state=TaskState.DONE)
        url = reverse("tasks:task-mark-done", args=[task.pk])
        expected_response = {
            "state": ["This task is already done."],
        }

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, expected_response)
