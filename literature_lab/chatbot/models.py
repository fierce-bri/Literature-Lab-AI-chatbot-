"""Database models for Literature Lab."""

from __future__ import annotations

import uuid

from django.db import models


class WritingInteraction(models.Model):
    """A successful writing-assistant request and its response."""

    class Task(models.TextChoices):
        ANALYZE = "analyze", "Analyze"
        BRAINSTORM = "brainstorm", "Brainstorm"
        IMPROVE = "improve", "Improve"
        CONTINUE = "continue", "Continue"

    class Genre(models.TextChoices):
        GENERAL = "general", "General"
        FANTASY = "fantasy", "Fantasy"
        SCIENCE_FICTION = (
            "science-fiction",
            "Science Fiction",
        )
        MYSTERY = "mystery", "Mystery"
        ROMANCE = "romance", "Romance"
        HORROR = "horror", "Horror"
        LITERARY_FICTION = (
            "literary-fiction",
            "Literary Fiction",
        )

    class Source(models.TextChoices):
        WEB = "web", "Web Interface"
        API = "api", "JSON API"

    request_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    input_text = models.TextField(
        max_length=10_000,
    )

    response_text = models.TextField()

    task = models.CharField(
        max_length=32,
        choices=Task.choices,
    )

    genre = models.CharField(
        max_length=32,
        choices=Genre.choices,
    )

    source = models.CharField(
        max_length=16,
        choices=Source.choices,
    )

    word_count = models.PositiveIntegerField()

    sentence_count = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "-created_at",
        )

        indexes = [
            models.Index(
                fields=["created_at"],
                name="chatbot_created_idx",
            ),
            models.Index(
                fields=["task", "genre"],
                name="chatbot_task_genre_idx",
            ),
        ]

    def __str__(self) -> str:
        """Return a short description for Django admin."""

        preview = " ".join(
            self.input_text.split()
        )

        if len(preview) > 60:
            preview = (
                preview[:57].rstrip()
                + "..."
            )

        return (
            f"{self.get_task_display()}: "
            f"{preview}"
        )
