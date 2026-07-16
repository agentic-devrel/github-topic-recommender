"""Topic normalization: canonical spelling, aliases, variant merging."""

from __future__ import annotations

import re
from collections import Counter

# Spelling variants that map onto an established GitHub topic name.
ALIASES = {
    "appsec": "application-security",
    "infosec": "information-security",
    "k8s": "kubernetes",
    "devtools": "developer-tools",
    "dev-tools": "developer-tools",
    "ci": "ci-cd",
    "cicd": "ci-cd",
    "ml": "machine-learning",
    "nlp": "natural-language-processing",
}

# Topics that carry no classification signal and are never recommended.
JUNK_TOPICS = frozenset(
    {
        "hacktoberfest",
        "hacktoberfest2024",
        "hacktoberfest2025",
        "awesome",
        "awesome-list",
        "awesome-lists",
        "good-first-issue",
        "help-wanted",
        "beginner-friendly",
        "first-timers-only",
        "up-for-grabs",
        "list",
        "lists",
        "resources",
    }
)

_HYPHEN_RUN_RE = re.compile(r"-{2,}")
_INVALID_CHAR_RE = re.compile(r"[^a-z0-9-]")


def normalize_topic(raw: str) -> str:
    """Normalize one topic string to GitHub's topic conventions.

    Returns "" when nothing usable remains.
    """
    topic = (raw or "").strip().lower()
    topic = topic.replace(" ", "-").replace("_", "-")
    topic = _INVALID_CHAR_RE.sub("", topic)
    topic = _HYPHEN_RUN_RE.sub("-", topic).strip("-")
    return ALIASES.get(topic, topic)


def _variant_key(topic: str) -> str:
    """Singular/plural variants share a key (developer-tool/developer-tools)."""
    if len(topic) > 4 and topic.endswith("s") and not topic.endswith("ss"):
        return topic[:-1]
    return topic


def merge_variants(counts: Counter[str]) -> dict[str, tuple[int, list[str]]]:
    """Merge singular/plural variants of the same topic.

    Returns {canonical: (combined_count, other_variants)} where the canonical
    spelling is the variant used most in the sample.
    """
    groups: dict[str, Counter[str]] = {}
    for topic, count in counts.items():
        groups.setdefault(_variant_key(topic), Counter())[topic] += count

    merged: dict[str, tuple[int, list[str]]] = {}
    for group in groups.values():
        canonical, _ = max(group.items(), key=lambda item: (item[1], item[0]))
        variants = sorted(t for t in group if t != canonical)
        merged[canonical] = (sum(group.values()), variants)
    return merged
