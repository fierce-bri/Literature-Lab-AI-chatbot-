"""Unit tests for the deterministic writing-assistant service."""

from django.test import SimpleTestCase

from ..services import (
    SUPPORTED_GENRES,
    SUPPORTED_TASKS,
    WritingAssistantService,
)


class WritingAssistantServiceTests(SimpleTestCase):
    """Verify writing guidance, normalization, and validation."""

    def setUp(self) -> None:
        """Create a fresh service for every test."""

        self.service = WritingAssistantService()

    def test_analyze_returns_structured_result(self) -> None:
        """Analyze should return guidance and accurate measurements."""

        result = self.service.generate_response(
            text=(
                "The city slept. "
                "Rain struck the windows."
            ),
            task="analyze",
            genre="mystery",
        )

        self.assertEqual(result.task, "analyze")
        self.assertEqual(result.genre, "mystery")
        self.assertEqual(result.word_count, 7)
        self.assertEqual(result.sentence_count, 2)
        self.assertIn(
            "Draft analysis",
            result.response,
        )
        self.assertIn(
            "Genre focus: Mystery",
            result.response,
        )
        self.assertIn(
            "Revision priorities",
            result.response,
        )

    def test_every_supported_task_generates_guidance(self) -> None:
        """All public task values should produce non-empty output."""

        text = (
            "A traveller entered the abandoned city. "
            "A light appeared inside the empty tower."
        )

        for task in SUPPORTED_TASKS:
            with self.subTest(task=task):
                result = self.service.generate_response(
                    text=text,
                    task=task,
                    genre="fantasy",
                )

                self.assertEqual(
                    result.task,
                    task,
                )
                self.assertTrue(
                    result.response.strip()
                )

    def test_every_supported_genre_is_accepted(self) -> None:
        """Every documented genre should be accepted by the service."""

        for genre in SUPPORTED_GENRES:
            with self.subTest(genre=genre):
                result = self.service.generate_response(
                    text=(
                        "A character discovers an unopened letter."
                    ),
                    task="brainstorm",
                    genre=genre,
                )

                self.assertEqual(
                    result.genre,
                    genre,
                )

    def test_task_and_genre_values_are_normalized(self) -> None:
        """Spaces, underscores, and casing should be normalized."""

        result = self.service.generate_response(
            text="A starship entered orbit.",
            task="  Brainstorm  ",
            genre="Science Fiction",
        )

        self.assertEqual(
            result.task,
            "brainstorm",
        )
        self.assertEqual(
            result.genre,
            "science-fiction",
        )

    def test_internal_whitespace_is_normalized(self) -> None:
        """Repeated whitespace should not affect text measurements."""

        result = self.service.generate_response(
            text=(
                "The   gate opened.\n\n"
                "A stranger entered."
            ),
            task="analyze",
            genre="general",
        )

        self.assertEqual(
            result.word_count,
            6,
        )
        self.assertEqual(
            result.sentence_count,
            2,
        )

    def test_empty_text_is_rejected(self) -> None:
        """Empty and whitespace-only drafts should fail."""

        for text in ("", "   ", "\n\t"):
            with self.subTest(text=repr(text)):
                with self.assertRaisesRegex(
                    ValueError,
                    "text must not be empty",
                ):
                    self.service.generate_response(
                        text=text,
                    )

    def test_oversized_text_is_rejected(self) -> None:
        """Input beyond the service limit should fail clearly."""

        text = (
            "a"
            * (
                self.service.max_input_characters
                + 1
            )
        )

        with self.assertRaisesRegex(
            ValueError,
            "text must not exceed",
        ):
            self.service.generate_response(
                text=text,
            )

    def test_non_string_text_is_rejected(self) -> None:
        """The core service should reject non-string input."""

        with self.assertRaisesRegex(
            TypeError,
            "text must be a string",
        ):
            self.service.generate_response(
                text=123,  # type: ignore[arg-type]
            )

    def test_unknown_task_is_rejected(self) -> None:
        """Unsupported task names should produce a useful error."""

        with self.assertRaisesRegex(
            ValueError,
            "task must be one of",
        ):
            self.service.generate_response(
                text="A valid writing idea.",
                task="rewrite-everything",
            )

    def test_unknown_genre_is_rejected(self) -> None:
        """Unsupported genres should produce a useful error."""

        with self.assertRaisesRegex(
            ValueError,
            "genre must be one of",
        ):
            self.service.generate_response(
                text="A valid writing idea.",
                genre="unknown-genre",
            )
