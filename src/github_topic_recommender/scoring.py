"""Topic aggregation, scoring signals, role assignment, and reasons."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone

from .models import ProjectProfile, Recommendation, Repo, TopicStats
from .normalize import JUNK_TOPICS, merge_variants, normalize_topic

WEIGHTS = {
    "prevalence": 0.40,
    "quality": 0.15,
    "relevance": 0.15,
    "specificity": 0.10,
    "cooccurrence": 0.10,
    "activity": 0.05,
}

# Broad terms that describe almost anything on GitHub; kept but penalized.
GENERIC_TOPICS = frozenset(
    {
        "open-source",
        "opensource",
        "github",
        "software",
        "tool",
        "tools",
        "app",
        "application",
        "project",
        "free",
        "code",
        "programming",
        "development",
        "developer",
        "utility",
        "utilities",
    }
)

LANGUAGE_TOPICS = frozenset(
    {
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        "golang",
        "rust",
        "ruby",
        "php",
        "c",
        "cpp",
        "csharp",
        "kotlin",
        "swift",
        "scala",
        "shell",
        "bash",
        "lua",
        "haskell",
        "elixir",
        "r",
        "julia",
        "zig",
    }
)

PROJECT_TYPE_TOPICS = frozenset(
    {
        "cli",
        "command-line",
        "command-line-tool",
        "command-line-interface",
        "library",
        "framework",
        "sdk",
        "api",
        "plugin",
        "extension",
        "web-app",
        "webapp",
        "desktop-app",
        "mobile-app",
        "server",
        "bot",
        "template",
        "boilerplate",
    }
)

GENERICITY_PENALTY = 0.35
ACTIVE_WINDOW_DAYS = 365
COOCCURRENCE_TOP_N = 25


def is_active(pushed_at: str | None, now: datetime) -> bool:
    if not pushed_at:
        return False
    try:
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return now - pushed <= timedelta(days=ACTIVE_WINDOW_DAYS)


def _usable_topics(repo: Repo) -> set[str]:
    topics = {normalize_topic(t) for t in repo.topics}
    return {t for t in topics if t and t not in JUNK_TOPICS}


def _profile_terms(profile: ProjectProfile) -> set[str]:
    terms: set[str] = set(profile.keywords)
    for source in [profile.name, *profile.existing_topics, *profile.languages]:
        cleaned = normalize_topic(source)
        if cleaned:
            terms.add(cleaned)
            terms.update(cleaned.split("-"))
    for keyword in profile.keywords:
        terms.update(keyword.split("-"))
    return terms


def _relevance(topic: str, terms: set[str]) -> float:
    if topic in terms:
        return 1.0
    tokens = topic.split("-")
    matched = sum(1 for token in tokens if token in terms)
    return matched / len(tokens)


def _specificity(topic: str) -> float:
    tokens = len(topic.split("-"))
    if tokens == 1:
        return 0.4
    if tokens == 2:
        return 0.7
    return 1.0


def score_topics(
    repos: list[Repo],
    profile: ProjectProfile,
    now: datetime | None = None,
) -> tuple[list[TopicStats], dict]:
    """Score every candidate topic found in the sample.

    Returns the stats sorted by score (descending) plus sample statistics for
    the report.
    """
    now = now or datetime.now(timezone.utc)
    active_flags = [is_active(repo.pushed_at, now) for repo in repos]
    raw_sets = [_usable_topics(repo) for repo in repos]

    counts: Counter[str] = Counter()
    for topic_set in raw_sets:
        counts.update(topic_set)
    merged = merge_variants(counts)
    canonical_of = {
        variant: canonical
        for canonical, (_, variants) in merged.items()
        for variant in [canonical, *variants]
    }

    topic_sets = [{canonical_of[t] for t in topic_set} for topic_set in raw_sets]
    repos_with_topics = sum(1 for topic_set in topic_sets if topic_set)

    sample = {
        "repositories_analyzed": len(repos),
        "repositories_with_topics": repos_with_topics,
        "active_repositories": sum(active_flags),
    }
    if repos_with_topics == 0:
        return [], sample

    star_mass: dict[str, float] = {}
    active_counts: Counter[str] = Counter()
    for repo, topic_set, active in zip(repos, topic_sets, active_flags):
        weight = math.log2(2 + repo.stargazers_count)
        for topic in topic_set:
            star_mass[topic] = star_mass.get(topic, 0.0) + weight
            if active:
                active_counts[topic] += 1

    merged_counts = {canonical: count for canonical, (count, _) in merged.items()}
    top_topics = {
        t for t, _ in Counter(merged_counts).most_common(COOCCURRENCE_TOP_N)
    }
    pair_counts: Counter[tuple[str, str]] = Counter()
    for topic_set in topic_sets:
        present = sorted(topic_set & top_topics)
        for i, first in enumerate(present):
            for second in present[i + 1 :]:
                pair_counts[(first, second)] += 1

    def cooccurrence(topic: str) -> float:
        others = top_topics - {topic}
        if not others or merged_counts[topic] == 0:
            return 0.0
        linked = sum(
            pair_counts[tuple(sorted((topic, other)))] for other in others
        )
        return min(1.0, linked / (merged_counts[topic] * max(1, len(others)) ** 0.5))

    terms = _profile_terms(profile)
    max_count = max(merged_counts.values())
    max_star_mass = max(star_mass.values())

    stats: list[TopicStats] = []
    for topic, count in merged_counts.items():
        prevalence = count / repos_with_topics
        components = {
            "prevalence": count / max_count,
            "quality": star_mass.get(topic, 0.0) / max_star_mass,
            "relevance": _relevance(topic, terms),
            "specificity": _specificity(topic),
            "cooccurrence": cooccurrence(topic) if topic in top_topics else 0.0,
            "activity": active_counts[topic] / count,
        }
        penalty = GENERICITY_PENALTY if topic in GENERIC_TOPICS else 0.0
        score = sum(WEIGHTS[name] * value for name, value in components.items()) - penalty
        stats.append(
            TopicStats(
                topic=topic,
                count=count,
                variants=merged[topic][1],
                prevalence=prevalence,
                quality=components["quality"],
                relevance=components["relevance"],
                specificity=components["specificity"],
                cooccurrence=components["cooccurrence"],
                activity=components["activity"],
                genericity_penalty=penalty,
                score=max(0.0, min(1.0, score)),
            )
        )

    stats.sort(key=lambda s: (-s.score, -s.count, s.topic))
    return stats, sample


def _role(stat: TopicStats, primary_assigned: bool) -> str:
    if stat.topic in LANGUAGE_TOPICS:
        return "language-ecosystem"
    if stat.topic in PROJECT_TYPE_TOPICS:
        return "project-type"
    if not primary_assigned and stat.relevance >= 0.5:
        return "primary-niche"
    if "-" not in stat.topic and stat.prevalence >= 0.15:
        return "category"
    if "-" in stat.topic and stat.relevance > 0.3:
        return "capability"
    return "related"


def _reason(stat: TopicStats, repos_with_topics: int) -> str:
    parts = [
        f"used by {stat.count} of {repos_with_topics} comparable repositories "
        f"({stat.prevalence:.0%})"
    ]
    if stat.relevance >= 0.5:
        parts.append("matches the project's own terminology")
    if stat.quality >= 0.75:
        parts.append("backed by high-star repositories")
    if stat.cooccurrence >= 0.5:
        parts.append("frequently co-assigned with other recommended topics")
    if stat.activity >= 0.6:
        parts.append("most of its repositories are recently active")
    if stat.genericity_penalty > 0:
        parts.append("broad term, ranked down for genericity")
    return "; ".join(parts)


def build_recommendations(
    stats: list[TopicStats], sample: dict, limit: int
) -> list[Recommendation]:
    repos_with_topics = sample.get("repositories_with_topics", 0)
    recommendations: list[Recommendation] = []
    primary_assigned = False
    for stat in stats[:limit]:
        role = _role(stat, primary_assigned)
        if role == "primary-niche":
            primary_assigned = True
        recommendations.append(
            Recommendation(
                topic=stat.topic,
                score=round(stat.score, 3),
                role=role,
                niche_prevalence=round(stat.prevalence, 3),
                repo_count=stat.count,
                reason=_reason(stat, repos_with_topics),
                variants=stat.variants,
            )
        )
    return recommendations
