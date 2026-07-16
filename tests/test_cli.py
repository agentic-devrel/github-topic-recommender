import json

import pytest

from github_topic_recommender.cli import main
from tests.fakes import DEVSECOPS_SAMPLE, FakeGitHubClient, repo_item


def make_client() -> FakeGitHubClient:
    return FakeGitHubClient(
        repo_data=repo_item(
            "me/pipeline-scanner",
            ["devsecops"],
            description="CLI that scans CI/CD pipelines for secrets",
        ),
        readme="Scans pipelines for secrets and vulnerable dependencies.",
        default_results=list(DEVSECOPS_SAMPLE),
    )


def test_analyze_json_output(capsys):
    exit_code = main(
        ["analyze", "me/pipeline-scanner", "--format", "json", "--limit", "5"],
        client=make_client(),
    )
    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["project"]["name"] == "me/pipeline-scanner"
    assert len(data["recommendations"]) <= 5


def test_analyze_rejects_non_owner_repo_target(capsys):
    exit_code = main(["analyze", "."], client=make_client())
    assert exit_code == 1
    assert "OWNER/REPOSITORY" in capsys.readouterr().err


def test_recommend_text_output(capsys):
    exit_code = main(
        ["recommend", "--description", "devsecops secret scanning CLI"],
        client=make_client(),
    )
    assert exit_code == 0
    assert "devsecops" in capsys.readouterr().out


def test_explore_markdown_output(capsys):
    exit_code = main(
        ["explore", "devsecops", "--format", "markdown"], client=make_client()
    )
    assert exit_code == 0
    assert "| Topic |" in capsys.readouterr().out


def test_github_error_exits_1(capsys):
    client = FakeGitHubClient(default_results=[])
    exit_code = main(
        ["recommend", "--description", "devsecops scanner"], client=client
    )
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_missing_command_exits_2():
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
