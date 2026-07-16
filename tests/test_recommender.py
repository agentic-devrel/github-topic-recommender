import pytest

from github_topic_recommender.github_client import GitHubError
from github_topic_recommender.recommender import Recommender
from tests.fakes import DEVSECOPS_SAMPLE, FakeGitHubClient, repo_item


def make_client(**kwargs) -> FakeGitHubClient:
    kwargs.setdefault("default_results", list(DEVSECOPS_SAMPLE))
    return FakeGitHubClient(**kwargs)


def test_analyze_repo_produces_report():
    client = make_client(
        repo_data=repo_item(
            "me/pipeline-scanner",
            ["devsecops"],
            description="CLI that scans CI/CD pipelines for secrets",
        ),
        readme="# pipeline-scanner\nScans pipelines for secrets and dependencies.",
    )
    report = Recommender(client).analyze_repo("me", "pipeline-scanner", limit=5)

    assert report.project["name"] == "me/pipeline-scanner"
    assert report.project["source"] == "github:me/pipeline-scanner"
    assert report.project["existing_topics"] == ["devsecops"]
    assert report.sample["repositories_analyzed"] == 8
    assert report.sample["queries"] == client.queries[: len(report.sample["queries"])]
    assert 1 <= len(report.recommendations) <= 5
    assert report.recommendations[0].topic == "devsecops"
    assert report.notes  # limitations are always disclosed


def test_analyze_repo_keeps_own_name_out_of_keywords():
    client = make_client(
        repo_data=repo_item(
            "me/pipeline-scanner",
            ["devsecops"],
            description="pipeline-scanner scans CI/CD pipelines for secrets",
        ),
        readme="pipeline-scanner pipeline-scanner pipeline-scanner",
    )
    report = Recommender(client).analyze_repo("me", "pipeline-scanner")
    assert "pipeline-scanner" not in report.project["keywords"]
    assert not any("pipeline-scanner" in q for q in client.queries)


def test_analyze_repo_excludes_itself_forks_and_archived():
    sample = [
        repo_item("me/self", ["devsecops"]),
        repo_item("other/fork", ["devsecops"], fork=True),
        repo_item("other/archived", ["devsecops"], archived=True),
        repo_item("other/kept", ["devsecops"]),
    ]
    client = make_client(
        repo_data=repo_item("me/self", [], description="devsecops secret scanner tool"),
        default_results=sample,
    )
    report = Recommender(client).analyze_repo("me", "self")
    assert report.sample["repositories_analyzed"] == 1


def test_collect_deduplicates_across_queries():
    client = FakeGitHubClient(
        search_results={
            "devsecops secrets scanner": [repo_item("a/one", ["devsecops"])],
            "devsecops secrets": [repo_item("a/one", ["devsecops"]), repo_item("b/two", ["ci-cd"])],
        },
        default_results=[],
    )
    report = Recommender(client).recommend_from_description(
        "devsecops secrets scanner"
    )
    assert report.sample["repositories_analyzed"] == 2


def test_max_repos_caps_sample():
    client = make_client()
    report = Recommender(client).recommend_from_description(
        "devsecops secret scanning pipelines", max_repos=3
    )
    assert report.sample["repositories_analyzed"] == 3


def test_explore_uses_niche_and_topic_query():
    client = make_client()
    Recommender(client).explore("AI security")
    assert client.queries[0] == "AI security"
    assert "topic:ai-security" in client.queries


def test_no_results_raises_github_error():
    client = FakeGitHubClient(default_results=[])
    with pytest.raises(GitHubError, match="No comparable repositories"):
        Recommender(client).recommend_from_description("devsecops scanner")


def test_blank_description_raises_github_error():
    client = make_client()
    with pytest.raises(GitHubError, match="Not enough project text"):
        Recommender(client).recommend_from_description("the of and")
