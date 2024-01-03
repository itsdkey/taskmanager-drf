from typing import Type

from django.db.models.query import QuerySet
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from tasks.filters import TaskFilterSet
from tasks.models import Task, TaskState
from tasks.permissions import IsTaskOwner
from tasks.serializers import TaskSerializer, TaskStateSerializer


@extend_schema_view(
    create=extend_schema(description="Create a new task for the logged-in user."),
    list=extend_schema(description="List out logged-in User's upcoming tasks."),
    retrieve=extend_schema(
        description="Get details of a specific task for the logged-in User.",
    ),
    update=extend_schema(
        description="Update a specific task related to the logged-in User.",
    ),
    partial_update=extend_schema(
        description="Update a specific task related to the logged-in User.",
    ),
    destroy=extend_schema(
        description="Delete a specific task related to the logged-in User.",
    ),
)
class TaskViewSet(ModelViewSet):
    """ViewSet to handle actions related to Task model."""

    permission_classes = (IsAuthenticated, IsTaskOwner)
    filterset_class = TaskFilterSet

    def get_queryset(self) -> QuerySet:
        if getattr(self, "swagger_fake_view", False):  # for drf-spectacular
            return Task.objects.none()

        user = self.request.user
        today = now()
        return Task.objects.filter(due_date__gte=today, owner=user).order_by("due_date")

    def get_serializer_class(self) -> Type[ModelSerializer]:
        serializers = {
            "mark_to_do": TaskStateSerializer,
            "mark_in_progress": TaskStateSerializer,
            "mark_done": TaskStateSerializer,
        }
        return serializers.get(self.action, TaskSerializer)

    @action(methods=["post"], detail=True)
    def mark_to_do(self, request: Request, pk: str = None) -> Response:
        return self._update_task_state(TaskState.TO_DO)

    @action(methods=["post"], detail=True)
    def mark_in_progress(self, request: Request, pk: str = None) -> Response:
        return self._update_task_state(TaskState.IN_PROGRESS)

    @action(methods=["post"], detail=True)
    def mark_done(self, request: Request, pk: str = None) -> Response:
        return self._update_task_state(TaskState.DONE)

    def _update_task_state(self, state: TaskState) -> Response:
        task = self.get_object()
        data = {"state": state}
        serializer = self.get_serializer(instance=task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
