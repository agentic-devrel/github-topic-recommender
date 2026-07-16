"""Pipeline orchestration: profile -> search -> score -> report."""

from __future__ import annotations

from datetime import datetime, timezone

from .github_client import GitHubClient, GitHubError
from .models import ProjectProfile, Repo, Report
from .normalize import normalize_topic
from .scoring import build_recommendations, score_topics
from .textutil import clean_text, extract_keywords

README_ANALYSIS_CHARS = 4000
DEFAULT_LIMIT = 10
DEFAULT_MAX_REPOS = 100

STANDING_NOTES = [
    "Global topic lift is not computed in the MVP; rankings rely on the "
    "sampled niche only.",
    "The sample comes from GitHub search sorted by stars and may not "
    "represent every repository in the niche.",
    "Assign only topics that the repository content genuinely supports.",
]


class Recommender:
    def __init__(self, client: GitHubClient):
        self.client = client

    def analyze_repo(
        self,
        owner: str,
        repo: str,
        limit: int = DEFAULT_LIMIT,
        max_repos: int = DEFAULT_MAX_REPOS,
    ) -> Report:
        data = self.client.get_repo(owner, repo)
        readme = clean_text(self.client.get_readme(owner, repo))
        description = data.get("description") or ""
        existing_topics = [
            t for t in (normalize_topic(x) for x in data.get("topics") or []) if t
        ]
        # Weight the description and topics above README prose; the repo's own
        # name identifies the project, not its niche, so keep it out of the
        # keywords used to build search queries.
        text = " ".join(
            [*([description] * 3), *existing_topics, readme[:README_ANALYSIS_CHARS]]
        )
        self_names = {owner.lower(), repo.lower(), data.get("name", "").lower()}
        profile = ProjectProfile(
            name=data.get("full_name", f"{owner}/{repo}"),
            description=description,
            keywords=[k for k in extract_keywords(text) if k not in self_names],
            languages=[data["language"]] if data.get("language") else [],
            existing_topics=existing_topics,
            source=f"github:{owner}/{repo}",
        )
        queries = self._build_queries(profile)
        return self._run(profile, queries, limit, max_repos, exclude=profile.name)

    def recommend_from_description(
        self,
        description: str,
        limit: int = DEFAULT_LIMIT,
        max_repos: int = DEFAULT_MAX_REPOS,
    ) -> Report:
        profile = ProjectProfile(
            name="project",
            description=description,
            keywords=extract_keywords(description),
            source="description",
        )
        queries = self._build_queries(profile)
        return self._run(profile, queries, limit, max_repos)

    def explore(
        self,
        niche: str,
        limit: int = DEFAULT_LIMIT,
        max_repos: int = DEFAULT_MAX_REPOS,
    ) -> Report:
        profile = ProjectProfile(
            name=niche,
            description=niche,
            keywords=extract_keywords(niche),
            source="niche",
        )
        queries = [niche]
        as_topic = normalize_topic(niche)
        if as_topic:
            queries.append(f"topic:{as_topic}")
        return self._run(profile, queries, limit, max_repos)

    def _build_queries(self, profile: ProjectProfile) -> list[str]:
        queries: list[str] = []
        keywords = profile.keywords
        if len(keywords) >= 3:
            queries.append(" ".join(keywords[:3]))
        for a, b in [(0, 1), (0, 2), (1, 2)]:
            if b < len(keywords):
                queries.append(f"{keywords[a]} {keywords[b]}")
        if not queries and keywords:
            queries.append(keywords[0])
        for topic in profile.existing_topics[:3]:
            queries.append(f"topic:{topic}")
        # Preserve order, drop duplicates.
        return list(dict.fromkeys(queries))

    def _collect(
        self, queries: list[str], max_repos: int, exclude: str | None
    ) -> list[Repo]:
        seen: dict[str, Repo] = {}
        max_pages = 1 if max_repos <= 50 else 2
        for query in queries:
            if len(seen) >= max_repos:
                break
            try:
                items = self.client.search_repositories(query, max_pages=max_pages)
            except GitHubError:
                if seen:
                    continue  # keep partial sample if later queries fail
                raise
            for item in items:
                repo = Repo.from_api(item)
                if repo.fork or repo.archived or not repo.full_name:
                    continue
                if exclude and repo.full_name.lower() == exclude.lower():
                    continue
                if repo.full_name not in seen:
                    seen[repo.full_name] = repo
                if len(seen) >= max_repos:
                    break
        return list(seen.values())

    def _run(
        self,
        profile: ProjectProfile,
        queries: list[str],
        limit: int,
        max_repos: int,
        exclude: str | None = None,
    ) -> Report:
        if not queries:
            raise GitHubError("Not enough project text to build search queries.")
        repos = self._collect(queries, max_repos, exclude)
        if not repos:
            raise GitHubError(
                "No comparable repositories found for: " + "; ".join(queries)
            )
        stats, sample = score_topics(repos, profile)
        recommendations = build_recommendations(stats, sample, limit)
        return Report(
            project={
                "name": profile.name,
                "source": profile.source,
                "description": profile.description,
                "languages": profile.languages,
                "existing_topics": profile.existing_topics,
                "keywords": profile.keywords[:8],
            },
            sample={
                **sample,
                "queries": queries,
                "collected_at": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
            },
            recommendations=recommendations,
            notes=list(STANDING_NOTES),
        )
