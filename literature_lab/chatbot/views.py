"""Browser and JSON API views for Literature Lab."""

from __future__ import annotations

import json

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from .forms import WritingAssistantForm
from .services import (
    WritingAssistantResult,
    WritingAssistantService,
)


writing_assistant = WritingAssistantService()


@require_http_methods(["GET", "POST"])
def assistant_view(request: HttpRequest) -> HttpResponse:
    """Render the browser-based writing-assistant interface."""

    form = WritingAssistantForm(
        request.POST
        if request.method == "POST"
        else None
    )

    result: WritingAssistantResult | None = None

    if request.method == "POST" and form.is_valid():
        try:
            result = writing_assistant.generate_response(
                text=form.cleaned_data["text"],
                task=form.cleaned_data["task"],
                genre=form.cleaned_data["genre"],
            )

        except (TypeError, ValueError) as error:
            form.add_error(None, str(error))

    return render(
        request,
        "chatbot/index.html",
        {
            "form": form,
            "result": result,
        },
    )


@require_GET
def health_api(request: HttpRequest) -> JsonResponse:
    """Confirm that the Literature Lab service is available."""

    return JsonResponse(
        {
            "status": "ok",
            "service": "literature-lab",
            "mode": "deterministic",
        }
    )


@csrf_exempt
@require_POST
def assistant_api(request: HttpRequest) -> JsonResponse:
    """Generate writing guidance from a JSON request.

    The endpoint is CSRF-exempt because it is intended to be called as a
    stateless JSON API rather than submitted through a Django HTML form.
    Authentication and rate limiting are not yet included.
    """

    if request.content_type != "application/json":
        return JsonResponse(
            {
                "detail": (
                    "Content-Type must be application/json."
                )
            },
            status=415,
        )

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )

    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse(
            {
                "detail": (
                    "Request body must contain valid JSON."
                )
            },
            status=400,
        )

    if not isinstance(payload, dict):
        return JsonResponse(
            {
                "detail": (
                    "The JSON request body must be an object."
                )
            },
            status=400,
        )

    allowed_fields = {
        "text",
        "task",
        "genre",
    }

    unexpected_fields = sorted(
        set(payload) - allowed_fields
    )

    if unexpected_fields:
        return JsonResponse(
            {
                "detail": "Unexpected request fields.",
                "fields": unexpected_fields,
            },
            status=422,
        )

    form = WritingAssistantForm(payload)

    if not form.is_valid():
        errors = {
            field: [
                error["message"]
                for error in field_errors
            ]
            for field, field_errors
            in form.errors.get_json_data().items()
        }

        return JsonResponse(
            {
                "detail": "Request validation failed.",
                "errors": errors,
            },
            status=422,
        )

    try:
        result = writing_assistant.generate_response(
            text=form.cleaned_data["text"],
            task=form.cleaned_data["task"],
            genre=form.cleaned_data["genre"],
        )

    except (TypeError, ValueError) as error:
        return JsonResponse(
            {
                "detail": str(error),
            },
            status=400,
        )

    return JsonResponse(
        {
            "response": result.response,
            "task": result.task,
            "genre": result.genre,
            "word_count": result.word_count,
            "sentence_count": result.sentence_count,
        }
    )
