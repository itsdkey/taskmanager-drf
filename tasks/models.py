from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskState(models.TextChoices):
    TO_DO = "TO_DO", _("to do")
    IN_PROGRESS = "IN_PROGRESS", _("in progress")
    DONE = "DONE", _("done")


class BaseModel(models.Model):
    """A base class that stores fields that will be used in inherited models."""

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class Task(BaseModel):
    owner = models.ForeignKey(
        verbose_name=_("user"),
        to="users.User",
        on_delete=models.CASCADE,
    )
    title = models.CharField(verbose_name=_("title"), max_length=128)
    description = models.TextField(verbose_name=_("description"))
    state = models.CharField(choices=TaskState.choices)
    due_date = models.DateField()
