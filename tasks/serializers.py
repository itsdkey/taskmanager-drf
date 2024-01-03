from datetime import date

from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault

from tasks.models import Task, TaskState


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=CurrentUserDefault(),
        write_only=True,
    )

    class Meta:
        model = Task
        fields = ["description", "due_date", "id", "owner", "state", "title"]
        read_only_fields = ["state"]

    def validate_due_date(self, due_date: date) -> date:
        if due_date < now().date():
            raise ValidationError("This date cannot be in the past.")
        return due_date

    def create(self, validated_data: dict) -> dict:
        validated_data["state"] = TaskState.TO_DO
        return super().create(validated_data)


class TaskStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["state"]

    def validate_state(self, state: TaskState) -> TaskState:
        if self.instance.state == TaskState.DONE:
            raise ValidationError("This task is already done.")
        return state

    def to_representation(self, instance: Task) -> dict:
        return TaskSerializer().to_representation(instance)
