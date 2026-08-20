"""Database-model tests for writing interaction history."""

from datetime import timedelta
from uuid import UUID

from django.test import TestCase
from django.utils import timezone

from ..models import WritingInteraction
from ..services import (
    SUPPORTED_GENRES,
    SUPPORTED_TASKS,
)


class WritingInteractionModelTests(TestCase):
    """Verify persisted writing-assistant interaction records."""

    def create_interaction(
        self,
        **overrides: object,
    ) -> WritingInteraction:
        """Create a valid interaction with optional field overrides."""

        values: dict[str, object] = {
            "input_text": (
                "A traveller entered the abandoned city."
            ),
            "response_text": (
                "Story-development directions"
            ),
            "task": WritingInteraction.Task.BRAINSTORM,
            "genre": WritingInteraction.Genre.FANTASY,
            "source": WritingInteraction.Source.WEB,
            "word_count": 6,
            "sentence_count": 1,
        }

        values.update(overrides)

        return WritingInteraction.objects.create(
            **values
        )

    def test_interaction_is_persisted(self) -> None:
        """All request metadata should be stored successfully."""

        interaction = self.create_interaction()

        self.assertIsInstance(
            interaction.request_id,
            UUID,
        )
        self.assertEqual(
            interaction.task,
            "brainstorm",
        )
        self.assertEqual(
            interaction.genre,
            "fantasy",
        )
        self.assertEqual(
            interaction.source,
            "web",
        )
        self.assertEqual(
            interaction.word_count,
            6,
        )
        self.assertEqual(
            interaction.sentence_count,
            1,
        )
        self.assertIsNotNone(
            interaction.created_at
        )

    def test_model_choices_match_service_values(self) -> None:
        """Database choices should remain synchronized with the service."""

        self.assertEqual(
            set(WritingInteraction.Task.values),
            set(SUPPORTED_TASKS),
        )
        self.assertEqual(
            set(WritingInteraction.Genre.values),
            set(SUPPORTED_GENRES),
        )

    def test_string_representation_contains_task_and_preview(
        self,
    ) -> None:
        """Admin descriptions should identify the task and input."""

        interaction = self.create_interaction(
            input_text="A traveller entered the city.",
            task=WritingInteraction.Task.ANALYZE,
        )

        self.assertEqual(
            str(interaction),
            (
                "Analyze: "
                "A traveller entered the city."
            ),
        )

    def test_long_string_representation_is_truncated(
        self,
    ) -> None:
        """Long draft text should not overwhelm Django admin."""

        interaction = self.create_interaction(
            input_text="word " * 40,
            task=WritingInteraction.Task.IMPROVE,
        )

        representation = str(interaction)

        self.assertTrue(
            representation.startswith(
                "Improve: "
            )
        )
        self.assertTrue(
            representation.endswith("...")
        )

    def test_default_ordering_is_newest_first(self) -> None:
        """Recent interactions should appear before older records."""

        older = self.create_interaction(
            input_text="Older interaction."
        )

        WritingInteraction.objects.filter(
            pk=older.pk
        ).update(
            created_at=(
                timezone.now()
                - timedelta(days=1)
            )
        )

        newer = self.create_interaction(
            input_text="Newer interaction."
        )

        interactions = list(
            WritingInteraction.objects.all()
        )

        self.assertEqual(
            interactions[0].pk,
            newer.pk,
        )
        self.assertEqual(
            interactions[1].pk,
            older.pk,
        )

    def test_request_ids_differ_between_interactions(
        self,
    ) -> None:
        """New records should receive independent UUID values."""

        first = self.create_interaction(
            input_text="First interaction."
        )
        second = self.create_interaction(
            input_text="Second interaction."
        )

        self.assertNotEqual(
            first.request_id,
            second.request_id,
        )
