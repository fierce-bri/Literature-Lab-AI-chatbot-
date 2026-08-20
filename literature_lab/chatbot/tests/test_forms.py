"""Tests for the Literature Lab browser and API form."""

from django.test import SimpleTestCase

from ..forms import WritingAssistantForm
from ..services import WritingAssistantService


class WritingAssistantFormTests(SimpleTestCase):
    """Verify user-input validation before service execution."""

    def test_valid_form(self) -> None:
        """A complete supported request should pass validation."""

        form = WritingAssistantForm(
            data={
                "text": (
                    "The traveller entered the abandoned city."
                ),
                "task": "brainstorm",
                "genre": "fantasy",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        self.assertEqual(
            form.cleaned_data["task"],
            "brainstorm",
        )
        self.assertEqual(
            form.cleaned_data["genre"],
            "fantasy",
        )

    def test_text_is_stripped(self) -> None:
        """Leading and trailing whitespace should be removed."""

        form = WritingAssistantForm(
            data={
                "text": "   A valid premise.   ",
                "task": "analyze",
                "genre": "general",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )
        self.assertEqual(
            form.cleaned_data["text"],
            "A valid premise.",
        )

    def test_unbound_form_has_browser_defaults(self) -> None:
        """The web form should initially select sensible values."""

        form = WritingAssistantForm()

        self.assertEqual(
            form["task"].value(),
            "analyze",
        )
        self.assertEqual(
            form["genre"].value(),
            "general",
        )

    def test_blank_text_is_invalid(self) -> None:
        """A blank draft should fail form validation."""

        form = WritingAssistantForm(
            data={
                "text": "   ",
                "task": "analyze",
                "genre": "general",
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        self.assertIn(
            "text",
            form.errors,
        )

    def test_text_over_character_limit_is_invalid(self) -> None:
        """The form and service should share the same input limit."""

        form = WritingAssistantForm(
            data={
                "text": (
                    "a"
                    * (
                        WritingAssistantService
                        .max_input_characters
                        + 1
                    )
                ),
                "task": "analyze",
                "genre": "general",
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        self.assertEqual(
            form.errors.as_data()["text"][0].code,
            "max_length",
        )

    def test_unsupported_task_is_invalid(self) -> None:
        """Unknown task values should be rejected by the form."""

        form = WritingAssistantForm(
            data={
                "text": "A valid premise.",
                "task": "unsupported-task",
                "genre": "general",
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        self.assertIn(
            "task",
            form.errors,
        )

    def test_unsupported_genre_is_invalid(self) -> None:
        """Unknown genre values should be rejected by the form."""

        form = WritingAssistantForm(
            data={
                "text": "A valid premise.",
                "task": "analyze",
                "genre": "western-space-opera",
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        self.assertIn(
            "genre",
            form.errors,
        )
