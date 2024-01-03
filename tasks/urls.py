from rest_framework import routers

from tasks.views import TaskViewSet

app_name = "tasks"

router = routers.SimpleRouter()

router.register(r"", TaskViewSet, basename="task")

urlpatterns = router.urls
