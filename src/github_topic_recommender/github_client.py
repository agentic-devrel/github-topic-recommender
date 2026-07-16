"""Thin client for the GitHub REST API endpoints the recommender needs."""

from __future__ import annotations

import os

import requests

API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"
DEFAULT_TIMEOUT = 30


class GitHubError(Exception):
    """Raised for GitHub API failures the CLI should report to the user."""


class GitHubClient:
    def __init__(self, token: str | None = None, session: requests.Session | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN") or None
        self.session = session or requests.Session()

    def _headers(self, accept: str = "application/vnd.github+json") -> dict[str, str]:
        headers = {
            "Accept": accept,
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "github-topic-recommender",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get(self, path: str, params: dict | None = None, accept: str | None = None):
        url = f"{API_BASE}{path}"
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._headers(accept) if accept else self._headers(),
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise GitHubError(f"GitHub request failed: {exc}") from exc

        if response.status_code == 404:
            raise GitHubError(f"Not found: {path}")
        if response.status_code in (403, 429):
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                raise GitHubError(
                    "GitHub API rate limit exceeded. Provide a token via "
                    "--token or the GITHUB_TOKEN environment variable."
                )
            raise GitHubError(f"GitHub API access denied ({response.status_code}) for {path}")
        if not response.ok:
            raise GitHubError(f"GitHub API error {response.status_code} for {path}")
        return response

    def get_repo(self, owner: str, repo: str) -> dict:
        return self._get(f"/repos/{owner}/{repo}").json()

    def get_readme(self, owner: str, repo: str) -> str:
        """Raw README content, or "" when the repository has none."""
        try:
            response = self._get(
                f"/repos/{owner}/{repo}/readme", accept="application/vnd.github.raw+json"
            )
        except GitHubError as exc:
            if "Not found" in str(exc):
                return ""
            raise
        return response.text

    def search_repositories(self, query: str, per_page: int = 50, max_pages: int = 2) -> list[dict]:
        """Repository search results (sorted by stars) across up to max_pages."""
        items: list[dict] = []
        for page in range(1, max_pages + 1):
            data = self._get(
                "/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page,
                    "page": page,
                },
            ).json()
            batch = data.get("items", [])
            items.extend(batch)
            if len(batch) < per_page:
                break
        return items
