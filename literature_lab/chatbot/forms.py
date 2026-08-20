"""Django form definitions for the Literature Lab writing assistant."""

from django import forms

from .services import (
    SUPPORTED_GENRES,
    SUPPORTED_TASKS,
    WritingAssistantService,
)


def _display_choice(value: str) -> str:
    """Convert a normalized service value into a readable label."""

    return value.replace("-", " ").title()


class WritingAssistantForm(forms.Form):
    """Validate writing-assistant input from the browser or JSON API."""

    text = forms.CharField(
        label="Draft, premise, or writing idea",
        min_length=1,
        max_length=WritingAssistantService.max_input_characters,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "rows": 14,
                "placeholder": (
                    "Paste a scene, paragraph, premise, or story idea..."
                ),
                "autocomplete": "off",
            }
        ),
    )

    task = forms.ChoiceField(
        choices=[
            (task, _display_choice(task))
            for task in SUPPORTED_TASKS
        ],
        initial="analyze",
    )

    genre = forms.ChoiceField(
        choices=[
            (genre, _display_choice(genre))
            for genre in SUPPORTED_GENRES
        ],
        initial="general",
    )
