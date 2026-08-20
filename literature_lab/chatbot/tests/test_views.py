"""Integration tests for Literature Lab browser and JSON routes."""

from __future__ import annotations

import json
from unittest.mock import patch
from uuid import UUID

from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from ..models import WritingInteraction


class BrowserViewTests(TestCase):
    """Verify the HTML writing-assistant workflow."""

    def setUp(self) -> None:
        """Resolve the browser route once per test."""

        self.url = reverse(
            "chatbot:home"
        )

    def test_home_page_loads(self) -> None:
        """The browser interface should be publicly reachable."""

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "chatbot/index.html",
        )
        self.assertContains(
            response,
            "Literature Lab",
        )
        self.assertContains(
            response,
            "Generate writing guidance",
        )

    def test_valid_browser_submission_creates_history(
        self,
    ) -> None:
        """Successful form submissions should be persisted."""

        response = self.client.post(
            self.url,
            data={
                "text": (
                    "The traveller reached the abandoned city."
                ),
                "task": "brainstorm",
                "genre": "fantasy",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "Writing guidance",
        )
        self.assertContains(
            response,
            "Story-development directions",
        )

        self.assertEqual(
            WritingInteraction.objects.count(),
            1,
        )

        interaction = (
            WritingInteraction.objects.get()
        )

        self.assertEqual(
            interaction.source,
            WritingInteraction.Source.WEB,
        )
        self.assertEqual(
            interaction.task,
            "brainstorm",
        )
        self.assertEqual(
            interaction.genre,
            "fantasy",
        )

    def test_invalid_browser_submission_is_not_saved(
        self,
    ) -> None:
        """Invalid form input should not create history records."""

        response = self.client.post(
            self.url,
            data={
                "text": "",
                "task": "analyze",
                "genre": "general",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTrue(
            response.context["form"].errors
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_service_error_is_displayed_and_not_saved(
        self,
    ) -> None:
        """Unexpected service validation errors should reach the form."""

        with patch(
            "chatbot.views."
            "writing_assistant.generate_response",
            side_effect=ValueError(
                "Unable to process this draft."
            ),
        ):
            response = self.client.post(
                self.url,
                data={
                    "text": "A valid draft.",
                    "task": "analyze",
                    "genre": "general",
                },
            )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "Unable to process this draft.",
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )


class HealthApiTests(TestCase):
    """Verify the JSON service-health route."""

    def test_health_endpoint(self) -> None:
        """The endpoint should identify the active service mode."""

        response = self.client.get(
            reverse(
                "chatbot:api-health"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "literature-lab",
                "mode": "deterministic",
            },
        )

    def test_health_endpoint_rejects_post(self) -> None:
        """The health endpoint should accept GET requests only."""

        response = self.client.post(
            reverse(
                "chatbot:api-health"
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class AssistantApiTests(TestCase):
    """Verify validation, responses, and persistence for the JSON API."""

    def setUp(self) -> None:
        """Resolve the API route and prepare one valid payload."""

        self.url = reverse(
            "chatbot:api-respond"
        )

        self.payload = {
            "text": (
                "The traveller reached the abandoned city. "
                "Rain darkened the road."
            ),
            "task": "brainstorm",
            "genre": "fantasy",
        }

    def post_json(
        self,
        payload: object,
    ):
        """Send a JSON request to the writing-assistant endpoint."""

        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_valid_request_returns_and_saves_result(
        self,
    ) -> None:
        """A successful API call should return traceable metadata."""

        response = self.post_json(
            self.payload
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        UUID(
            body["request_id"]
        )

        self.assertIsNotNone(
            parse_datetime(
                body["created_at"]
            )
        )
        self.assertEqual(
            body["task"],
            "brainstorm",
        )
        self.assertEqual(
            body["genre"],
            "fantasy",
        )
        self.assertTrue(
            body["response"]
        )
        self.assertGreater(
            body["word_count"],
            0,
        )
        self.assertEqual(
            body["sentence_count"],
            2,
        )

        self.assertEqual(
            WritingInteraction.objects.count(),
            1,
        )

        interaction = (
            WritingInteraction.objects.get()
        )

        self.assertEqual(
            interaction.source,
            WritingInteraction.Source.API,
        )
        self.assertEqual(
            str(interaction.request_id),
            body["request_id"],
        )
        self.assertEqual(
            interaction.input_text,
            self.payload["text"],
        )

    def test_non_json_content_type_is_rejected(
        self,
    ) -> None:
        """The endpoint should require an explicit JSON content type."""

        response = self.client.post(
            self.url,
            data="plain text",
            content_type="text/plain",
        )

        self.assertEqual(
            response.status_code,
            415,
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_malformed_json_is_rejected(self) -> None:
        """Invalid JSON syntax should produce HTTP 400."""

        response = self.client.post(
            self.url,
            data="{invalid",
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_non_object_json_is_rejected(self) -> None:
        """JSON arrays should not be treated as request objects."""

        response = self.post_json(
            [
                "not",
                "an",
                "object",
            ]
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_unexpected_fields_are_rejected(
        self,
    ) -> None:
        """Unknown properties should not be silently ignored."""

        payload = {
            **self.payload,
            "unknown_field": True,
        }

        response = self.post_json(
            payload
        )

        self.assertEqual(
            response.status_code,
            422,
        )
        self.assertEqual(
            response.json()["fields"],
            [
                "unknown_field",
            ],
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_missing_text_is_rejected(self) -> None:
        """Required text should be checked by the shared Django form."""

        response = self.post_json(
            {
                "task": "analyze",
                "genre": "general",
            }
        )

        self.assertEqual(
            response.status_code,
            422,
        )
        self.assertIn(
            "text",
            response.json()["errors"],
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_invalid_task_is_rejected(self) -> None:
        """Unsupported task values should produce HTTP 422."""

        response = self.post_json(
            {
                **self.payload,
                "task": "rewrite-everything",
            }
        )

        self.assertEqual(
            response.status_code,
            422,
        )
        self.assertIn(
            "task",
            response.json()["errors"],
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_service_error_becomes_http_400(
        self,
    ) -> None:
        """Service errors should not leak as unhandled server errors."""

        with patch(
            "chatbot.views."
            "writing_assistant.generate_response",
            side_effect=ValueError(
                "Unable to process this draft."
            ),
        ):
            response = self.post_json(
                self.payload
            )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json(),
            {
                "detail": (
                    "Unable to process this draft."
                )
            },
        )
        self.assertEqual(
            WritingInteraction.objects.count(),
            0,
        )

    def test_get_method_is_rejected(self) -> None:
        """The response endpoint should accept POST requests only."""

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            405,
        )
