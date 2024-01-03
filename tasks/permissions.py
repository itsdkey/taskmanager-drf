from typing import Any

from rest_framework import permissions
from rest_framework.request import Request

from tasks.models import Task


class IsTaskOwner(permissions.BasePermission):
    """Permission that checks if the logged-in User is the task's owner."""

    def has_object_permission(self, request: Request, view: Any, obj: Task) -> bool:
        return obj.owner_id == request.user.id
