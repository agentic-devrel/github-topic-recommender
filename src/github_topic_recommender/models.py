"""Dataclasses shared across the recommendation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Repo:
    """A comparable GitHub repository from the search sample."""

    full_name: str
    description: str = ""
    topics: list[str] = field(default_factory=list)
    language: str | None = None
    stargazers_count: int = 0
    forks_count: int = 0
    pushed_at: str | None = None
    fork: bool = False
    archived: bool = False
    html_url: str = ""

    @classmethod
    def from_api(cls, data: dict) -> "Repo":
        return cls(
            full_name=data.get("full_name", ""),
            description=data.get("description") or "",
            topics=list(data.get("topics") or []),
            language=data.get("language"),
            stargazers_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            pushed_at=data.get("pushed_at"),
            fork=bool(data.get("fork", False)),
            archived=bool(data.get("archived", False)),
            html_url=data.get("html_url", ""),
        )


@dataclass
class ProjectProfile:
    """What we know about the project being analyzed."""

    name: str
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    existing_topics: list[str] = field(default_factory=list)
    source: str = "description"


@dataclass
class TopicStats:
    """Aggregated evidence and scoring signals for one candidate topic."""

    topic: str
    count: int = 0
    variants: list[str] = field(default_factory=list)
    prevalence: float = 0.0  # share of sampled repos (with topics) using it
    quality: float = 0.0
    relevance: float = 0.0
    specificity: float = 0.0
    cooccurrence: float = 0.0
    activity: float = 0.0
    genericity_penalty: float = 0.0
    score: float = 0.0


@dataclass
class Recommendation:
    topic: str
    score: float
    role: str
    niche_prevalence: float
    repo_count: int
    reason: str
    variants: list[str] = field(default_factory=list)


@dataclass
class Report:
    project: dict
    sample: dict
    recommendations: list[Recommendation]
    notes: list[str] = field(default_factory=list)
