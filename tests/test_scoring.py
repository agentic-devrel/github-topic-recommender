from datetime import datetime, timezone

from github_topic_recommender.models import ProjectProfile, Repo
from github_topic_recommender.scoring import (
    build_recommendations,
    is_active,
    score_topics,
)
from tests.fakes import DEVSECOPS_SAMPLE

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)

PROFILE = ProjectProfile(
    name="pipeline-scanner",
    description="CLI that scans CI/CD pipelines for secrets and dependencies",
    keywords=["devsecops", "secrets", "scanning", "ci-cd", "dependencies"],
    languages=["Python"],
    source="description",
)


def _repos() -> list[Repo]:
    return [Repo.from_api(item) for item in DEVSECOPS_SAMPLE]


def test_is_active_window():
    assert is_active("2026-06-01T00:00:00Z", NOW)
    assert not is_active("2023-01-01T00:00:00Z", NOW)
    assert not is_active(None, NOW)
    assert not is_active("not-a-date", NOW)


def test_sample_statistics():
    _, sample = score_topics(_repos(), PROFILE, now=NOW)
    assert sample["repositories_analyzed"] == 8
    # misc/awesome-security only has junk topics; misc/no-topics has none.
    assert sample["repositories_with_topics"] == 6
    assert sample["active_repositories"] == 7


def test_relevant_prevalent_topic_ranks_first():
    stats, _ = score_topics(_repos(), PROFILE, now=NOW)
    assert stats[0].topic == "devsecops"
    assert stats[0].prevalence == 5 / 6


def test_junk_topics_are_excluded():
    stats, _ = score_topics(_repos(), PROFILE, now=NOW)
    topics = {s.topic for s in stats}
    assert "hacktoberfest" not in topics
    assert "awesome" not in topics


def test_generic_topics_are_penalized():
    stats, _ = score_topics(_repos(), PROFILE, now=NOW)
    by_topic = {s.topic: s for s in stats}
    generic = by_topic["open-source"]
    assert generic.genericity_penalty > 0
    # Same single-repo count as sbom, but ranked below it.
    assert generic.score < by_topic["sbom"].score


def test_empty_sample_returns_no_stats():
    repos = [Repo(full_name="a/b", topics=[])]
    stats, sample = score_topics(repos, PROFILE, now=NOW)
    assert stats == []
    assert sample["repositories_with_topics"] == 0


def test_build_recommendations_limits_and_explains():
    stats, sample = score_topics(_repos(), PROFILE, now=NOW)
    recommendations = build_recommendations(stats, sample, limit=3)
    assert len(recommendations) == 3
    top = recommendations[0]
    assert top.topic == "devsecops"
    assert top.role == "primary-niche"
    assert "5 of 6 comparable repositories" in top.reason
    assert 0.0 <= top.score <= 1.0


def test_roles_for_project_type_topics():
    stats, sample = score_topics(_repos(), PROFILE, now=NOW)
    recommendations = build_recommendations(stats, sample, limit=10)
    roles = {r.topic: r.role for r in recommendations}
    assert roles.get("cli") == "project-type"
