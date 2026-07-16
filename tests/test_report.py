import json

import pytest

from github_topic_recommender.models import Recommendation, Report
from github_topic_recommender.report import render


@pytest.fixture
def report() -> Report:
    return Report(
        project={"name": "me/scanner", "source": "github:me/scanner"},
        sample={
            "repositories_analyzed": 8,
            "repositories_with_topics": 6,
            "active_repositories": 7,
            "queries": ["devsecops scanner"],
            "collected_at": "2026-07-16T00:00:00+00:00",
        },
        recommendations=[
            Recommendation(
                topic="devsecops",
                score=0.91,
                role="primary-niche",
                niche_prevalence=0.833,
                repo_count=5,
                reason="used by 5 of 6 comparable repositories (83%)",
            )
        ],
        notes=["Sample may not represent every repository in the niche."],
    )


def test_render_json_shape(report):
    data = json.loads(render(report, "json"))
    assert data["project"]["name"] == "me/scanner"
    assert data["sample"]["repositories_analyzed"] == 8
    rec = data["recommendations"][0]
    assert rec["topic"] == "devsecops"
    assert rec["score"] == 0.91
    assert rec["role"] == "primary-niche"
    assert rec["niche_prevalence"] == 0.833
    assert rec["reason"]


def test_render_text_lists_topics_and_notes(report):
    text = render(report, "text")
    assert "me/scanner" in text
    assert "devsecops" in text
    assert "8 repositories analyzed" in text
    assert "Notes:" in text


def test_render_markdown_has_table(report):
    markdown = render(report, "markdown")
    assert "| Topic | Score | Role | Prevalence | Why it fits |" in markdown
    assert "| `devsecops` | 0.91 | primary-niche | 83% |" in markdown


def test_render_unknown_format_raises(report):
    with pytest.raises(ValueError, match="Unknown format"):
        render(report, "yaml")
