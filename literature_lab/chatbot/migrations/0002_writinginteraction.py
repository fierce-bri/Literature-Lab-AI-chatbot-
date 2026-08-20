"""Upgrade UserQuery into the WritingInteraction history model."""

import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "chatbot",
            "0001_initial",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UserQuery",
            new_name="WritingInteraction",
        ),

        migrations.AlterField(
            model_name="writinginteraction",
            name="input_text",
            field=models.TextField(
                max_length=10_000,
            ),
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="request_id",
            field=models.UUIDField(
                db_index=True,
                default=uuid.uuid4,
                editable=False,
            ),
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="task",
            field=models.CharField(
                choices=[
                    ("analyze", "Analyze"),
                    ("brainstorm", "Brainstorm"),
                    ("improve", "Improve"),
                    ("continue", "Continue"),
                ],
                default="analyze",
                max_length=32,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="genre",
            field=models.CharField(
                choices=[
                    ("general", "General"),
                    ("fantasy", "Fantasy"),
                    (
                        "science-fiction",
                        "Science Fiction",
                    ),
                    ("mystery", "Mystery"),
                    ("romance", "Romance"),
                    ("horror", "Horror"),
                    (
                        "literary-fiction",
                        "Literary Fiction",
                    ),
                ],
                default="general",
                max_length=32,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="source",
            field=models.CharField(
                choices=[
                    ("web", "Web Interface"),
                    ("api", "JSON API"),
                ],
                default="web",
                max_length=16,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="word_count",
            field=models.PositiveIntegerField(
                default=0,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="sentence_count",
            field=models.PositiveIntegerField(
                default=0,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="writinginteraction",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),

        migrations.AlterModelOptions(
            name="writinginteraction",
            options={
                "ordering": (
                    "-created_at",
                ),
            },
        ),

        migrations.AddIndex(
            model_name="writinginteraction",
            index=models.Index(
                fields=["created_at"],
                name="chatbot_created_idx",
            ),
        ),

        migrations.AddIndex(
            model_name="writinginteraction",
            index=models.Index(
                fields=[
                    "task",
                    "genre",
                ],
                name="chatbot_task_genre_idx",
            ),
        ),
    ]
