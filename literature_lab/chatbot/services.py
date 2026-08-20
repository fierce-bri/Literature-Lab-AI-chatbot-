"""Core writing-assistant logic for Literature Lab.

The current service is deterministic and does not require an external
language-model provider. It provides a reliable local foundation that can
later be extended with an optional LLM integration.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final


SUPPORTED_TASKS: Final[tuple[str, ...]] = (
    "analyze",
    "brainstorm",
    "improve",
    "continue",
)

SUPPORTED_GENRES: Final[tuple[str, ...]] = (
    "general",
    "fantasy",
    "science-fiction",
    "mystery",
    "romance",
    "horror",
    "literary-fiction",
)

SENSORY_WORDS: Final[frozenset[str]] = frozenset(
    {
        "bright",
        "dark",
        "dim",
        "glow",
        "shadow",
        "red",
        "blue",
        "green",
        "cold",
        "warm",
        "hot",
        "rough",
        "smooth",
        "soft",
        "hard",
        "silent",
        "quiet",
        "loud",
        "whisper",
        "shout",
        "smell",
        "scent",
        "taste",
        "bitter",
        "sweet",
        "smoke",
        "rain",
        "wind",
        "blood",
    }
)


@dataclass(frozen=True)
class WritingAssistantResult:
    """Structured result returned by the writing-assistant service."""

    response: str
    task: str
    genre: str
    word_count: int
    sentence_count: int


class WritingAssistantService:
    """Generate structured writing guidance from a supplied draft."""

    max_input_characters = 10_000

    def generate_response(
        self,
        text: str,
        task: str = "analyze",
        genre: str = "general",
    ) -> WritingAssistantResult:
        """Generate writing feedback or planning guidance.

        Args:
            text:
                Draft, premise, paragraph, or writing idea supplied by
                the user.

            task:
                One of ``analyze``, ``brainstorm``, ``improve``, or
                ``continue``.

            genre:
                A supported genre used to tailor the guidance.

        Returns:
            A structured WritingAssistantResult.

        Raises:
            TypeError:
                If the supplied text is not a string.

            ValueError:
                If the input is empty, too long, or contains an
                unsupported task or genre.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        cleaned_text = self._normalize_text(text)

        if not cleaned_text:
            raise ValueError("text must not be empty")

        if len(cleaned_text) > self.max_input_characters:
            raise ValueError(
                "text must not exceed "
                f"{self.max_input_characters:,} characters"
            )

        normalized_task = self._normalize_choice(task)

        if normalized_task not in SUPPORTED_TASKS:
            raise ValueError(
                "task must be one of: "
                + ", ".join(SUPPORTED_TASKS)
            )

        normalized_genre = self._normalize_choice(genre)

        if normalized_genre not in SUPPORTED_GENRES:
            raise ValueError(
                "genre must be one of: "
                + ", ".join(SUPPORTED_GENRES)
            )

        sentences = self._split_sentences(cleaned_text)
        words = self._extract_words(cleaned_text)

        response_generators = {
            "analyze": self._analyze,
            "brainstorm": self._brainstorm,
            "improve": self._improve,
            "continue": self._continue,
        }

        response = response_generators[normalized_task](
            cleaned_text,
            sentences,
            words,
            normalized_genre,
        )

        return WritingAssistantResult(
            response=response,
            task=normalized_task,
            genre=normalized_genre,
            word_count=len(words),
            sentence_count=len(sentences),
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Remove unnecessary whitespace while preserving the content."""

        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _normalize_choice(value: str) -> str:
        """Normalize task and genre values used by the service."""

        return (
            str(value)
            .strip()
            .lower()
            .replace("_", "-")
            .replace(" ", "-")
        )

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences without external NLP downloads."""

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def _extract_words(text: str) -> list[str]:
        """Return lowercase words from the supplied text."""

        return re.findall(
            r"[A-Za-zÀ-ÖØ-öø-ÿ']+",
            text.lower(),
        )

    def _analyze(
        self,
        text: str,
        sentences: list[str],
        words: list[str],
        genre: str,
    ) -> str:
        """Generate a concise structural analysis of the draft."""

        word_count = len(words)
        sentence_count = len(sentences)
        average_length = (
            word_count / sentence_count
            if sentence_count
            else 0
        )

        dialogue_detected = (
            '"' in text
            or "“" in text
            or "”" in text
        )

        sensory_count = sum(
            word in SENSORY_WORDS
            for word in words
        )

        priorities = self._revision_priorities(
            word_count=word_count,
            average_sentence_length=average_length,
            dialogue_detected=dialogue_detected,
            sensory_count=sensory_count,
        )

        return "\n".join(
            [
                "Draft analysis",
                "",
                f"Genre focus: {self._display_genre(genre)}",
                f"Word count: {word_count}",
                f"Sentence count: {sentence_count}",
                (
                    "Average sentence length: "
                    f"{average_length:.1f} words"
                ),
                (
                    "Dialogue detected: "
                    f"{'yes' if dialogue_detected else 'no'}"
                ),
                f"Sensory-language signals: {sensory_count}",
                "",
                "Revision priorities",
                *[
                    f"{index}. {priority}"
                    for index, priority in enumerate(
                        priorities,
                        start=1,
                    )
                ],
            ]
        )

    def _improve(
        self,
        text: str,
        sentences: list[str],
        words: list[str],
        genre: str,
    ) -> str:
        """Generate practical revision guidance."""

        average_length = (
            len(words) / len(sentences)
            if sentences
            else 0
        )

        dialogue_detected = (
            '"' in text
            or "“" in text
            or "”" in text
        )

        sensory_count = sum(
            word in SENSORY_WORDS
            for word in words
        )

        priorities = self._revision_priorities(
            word_count=len(words),
            average_sentence_length=average_length,
            dialogue_detected=dialogue_detected,
            sensory_count=sensory_count,
        )

        genre_note = self._genre_guidance(genre)

        return "\n".join(
            [
                "Revision plan",
                "",
                f"Genre lens: {self._display_genre(genre)}",
                "",
                *[
                    f"{index}. {priority}"
                    for index, priority in enumerate(
                        priorities,
                        start=1,
                    )
                ],
                "",
                "Genre-specific consideration",
                genre_note,
                "",
                "Final editing pass",
                (
                    "Replace vague verbs and general nouns with precise "
                    "actions, concrete objects, and character-specific "
                    "details."
                ),
            ]
        )

    def _brainstorm(
        self,
        text: str,
        sentences: list[str],
        words: list[str],
        genre: str,
    ) -> str:
        """Generate three directions for developing an idea."""

        premise = sentences[0]

        if len(premise) > 180:
            premise = premise[:177].rstrip() + "..."

        return "\n".join(
            [
                "Story-development directions",
                "",
                f"Starting point: {premise}",
                f"Genre lens: {self._display_genre(genre)}",
                "",
                (
                    "1. Conflict direction: Introduce an obstacle that "
                    "directly threatens what the central character wants."
                ),
                (
                    "2. Character direction: Force the character to "
                    "choose between two outcomes that both carry a cost."
                ),
                (
                    "3. Discovery direction: Reveal information that "
                    "changes the meaning of an earlier event or belief."
                ),
                "",
                "Genre-specific possibility",
                self._genre_guidance(genre),
                "",
                (
                    "Development question: What would make the next "
                    "decision emotionally difficult rather than merely "
                    "logistically difficult?"
                ),
            ]
        )

    def _continue(
        self,
        text: str,
        sentences: list[str],
        words: list[str],
        genre: str,
    ) -> str:
        """Generate a continuation outline rather than invented prose."""

        final_sentence = sentences[-1]

        if len(final_sentence) > 180:
            final_sentence = (
                final_sentence[:177].rstrip()
                + "..."
            )

        return "\n".join(
            [
                "Next-scene blueprint",
                "",
                f"Current endpoint: {final_sentence}",
                f"Genre lens: {self._display_genre(genre)}",
                "",
                (
                    "1. Immediate consequence: Show how the final action "
                    "or revelation changes the character's situation."
                ),
                (
                    "2. Character response: Give the character a clear "
                    "emotional reaction followed by a deliberate choice."
                ),
                (
                    "3. Escalation: Add a new complication, cost, deadline, "
                    "or opposing goal."
                ),
                (
                    "4. Scene hook: End the next section with a question, "
                    "discovery, reversal, or unresolved decision."
                ),
                "",
                "Genre-specific direction",
                self._genre_guidance(genre),
            ]
        )

    @staticmethod
    def _revision_priorities(
        word_count: int,
        average_sentence_length: float,
        dialogue_detected: bool,
        sensory_count: int,
    ) -> list[str]:
        """Select useful revision priorities from draft measurements."""

        priorities: list[str] = []

        if average_sentence_length > 24:
            priorities.append(
                "Break up some long sentences so important actions and "
                "images receive more emphasis."
            )
        elif average_sentence_length < 8:
            priorities.append(
                "Combine selected short sentences to create smoother "
                "rhythm and stronger relationships between ideas."
            )
        else:
            priorities.append(
                "Vary sentence length deliberately to control pace and "
                "emphasis."
            )

        if sensory_count < 2:
            priorities.append(
                "Add one or two concrete sensory details that establish "
                "place, atmosphere, or physical experience."
            )
        else:
            priorities.append(
                "Keep the strongest sensory details and remove any that "
                "do not support mood, character, or action."
            )

        if not dialogue_detected:
            priorities.append(
                "Consider whether dialogue, internal thought, or a "
                "specific character reaction could make the scene feel "
                "more immediate."
            )
        else:
            priorities.append(
                "Check that each line of dialogue reveals intention, "
                "conflict, character, or new information."
            )

        if word_count < 40:
            priorities.append(
                "Clarify the central character's immediate goal and the "
                "obstacle preventing it."
            )

        return priorities[:3]

    @staticmethod
    def _genre_guidance(genre: str) -> str:
        """Return a focused development prompt for the selected genre."""

        guidance = {
            "general": (
                "Strengthen the relationship between the character's "
                "goal, the obstacle, and the consequence of failure."
            ),
            "fantasy": (
                "Reveal a rule, cost, history, or cultural consequence "
                "behind the fantastical element."
            ),
            "science-fiction": (
                "Connect the technology or scientific idea to a human, "
                "ethical, political, or social consequence."
            ),
            "mystery": (
                "Introduce a clue that is visible but open to more than "
                "one interpretation."
            ),
            "romance": (
                "Create tension between emotional desire, vulnerability, "
                "and the risk of honest communication."
            ),
            "horror": (
                "Use uncertainty, limited information, and specific "
                "sensory details to increase dread."
            ),
            "literary-fiction": (
                "Use action, image, and subtext to connect the external "
                "scene with the character's internal conflict."
            ),
        }

        return guidance[genre]

    @staticmethod
    def _display_genre(genre: str) -> str:
        """Convert a normalized genre value into display text."""

        return genre.replace("-", " ").title()
