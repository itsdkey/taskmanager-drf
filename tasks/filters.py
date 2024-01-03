from django_filters import rest_framework as filters

from tasks.models import Task


class TaskFilterSet(filters.FilterSet):
    class Meta:
        model = Task
        fields = ["due_date"]
