from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "due_date", "title", "state"]
    list_filter = ("owner",)
    raw_id_fields = ["owner"]
    ordering = ("owner",)
