"""Offline fakes and fixtures shared across the test suite."""

from __future__ import annotations

from github_topic_recommender.github_client import GitHubError


def repo_item(
    full_name: str,
    topics: list[str],
    stars: int = 100,
    description: str = "",
    language: str = "Python",
    pushed_at: str = "2026-06-01T00:00:00Z",
    fork: bool = False,
    archived: bool = False,
) -> dict:
    return {
        "full_name": full_name,
        "name": full_name.split("/")[-1],
        "description": description,
        "topics": topics,
        "language": language,
        "stargazers_count": stars,
        "forks_count": stars // 10,
        "pushed_at": pushed_at,
        "fork": fork,
        "archived": archived,
        "html_url": f"https://github.com/{full_name}",
    }


DEVSECOPS_SAMPLE = [
    repo_item("acme/pipeline-guard", ["devsecops", "secret-scanning", "ci-cd"], stars=4200),
    repo_item("acme/dep-check", ["devsecops", "dependency-scanning", "security-tools"], stars=1800),
    repo_item("orga/secretshound", ["secret-scanning", "devsecops", "cli"], stars=950),
    repo_item("orga/sbom-forge", ["sbom", "supply-chain-security", "devsecops"], stars=760),
    repo_item("solo/scanner", ["security-tools", "devsecops", "open-source"], stars=310),
    repo_item("solo/oldscan", ["security"], stars=90, pushed_at="2023-01-01T00:00:00Z"),
    repo_item("misc/awesome-security", ["awesome", "hacktoberfest"], stars=8000),
    repo_item("misc/no-topics", [], stars=40),
]


class FakeGitHubClient:
    """Stands in for GitHubClient without any network access."""

    def __init__(
        self,
        repo_data: dict | None = None,
        readme: str = "",
        search_results: dict[str, list[dict]] | None = None,
        default_results: list[dict] | None = None,
    ):
        self.repo_data = repo_data
        self.readme = readme
        self.search_results = search_results or {}
        self.default_results = default_results if default_results is not None else []
        self.queries: list[str] = []

    def get_repo(self, owner: str, repo: str) -> dict:
        if self.repo_data is None:
            raise GitHubError(f"Not found: /repos/{owner}/{repo}")
        return self.repo_data

    def get_readme(self, owner: str, repo: str) -> str:
        return self.readme

    def search_repositories(self, query: str, per_page: int = 50, max_pages: int = 2):
        self.queries.append(query)
        return list(self.search_results.get(query, self.default_results))
