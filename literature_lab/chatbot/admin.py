"""Django admin configuration for Literature Lab."""

from django.contrib import admin
from django.http import HttpRequest

from .models import WritingInteraction


@admin.register(WritingInteraction)
class WritingInteractionAdmin(admin.ModelAdmin):
    """Read-only administration view for writing interactions."""

    list_display = (
        "short_request_id",
        "task",
        "genre",
        "source",
        "word_count",
        "sentence_count",
        "created_at",
    )

    list_filter = (
        "task",
        "genre",
        "source",
        "created_at",
    )

    search_fields = (
        "input_text",
        "response_text",
    )

    readonly_fields = (
        "request_id",
        "input_text",
        "response_text",
        "task",
        "genre",
        "source",
        "word_count",
        "sentence_count",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    @admin.display(
        description="Request ID",
    )
    def short_request_id(
        self,
        interaction: WritingInteraction,
    ) -> str:
        """Display a compact request identifier."""

        return str(
            interaction.request_id
        )[:8]

    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        """Interaction records are created by the application."""

        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: WritingInteraction | None = None,
    ) -> bool:
        """Interaction history should not be edited manually."""

        return False
