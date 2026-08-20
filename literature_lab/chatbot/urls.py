"""URL routes for the Literature Lab writing assistant."""

from django.urls import path

from . import views


app_name = "chatbot"


urlpatterns = [
    path(
        "",
        views.assistant_view,
        name="home",
    ),
    path(
        "api/v1/health/",
        views.health_api,
        name="api-health",
    ),
    path(
        "api/v1/respond/",
        views.assistant_api,
        name="api-respond",
    ),
]
