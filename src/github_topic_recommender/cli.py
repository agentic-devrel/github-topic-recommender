"""Command-line interface for github-topic-recommender."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .github_client import GitHubClient, GitHubError
from .recommender import DEFAULT_LIMIT, DEFAULT_MAX_REPOS, Recommender
from .report import FORMATS, render


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"maximum number of recommended topics (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--format",
        choices=FORMATS,
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=DEFAULT_MAX_REPOS,
        help=f"maximum comparable repositories to sample (default: {DEFAULT_MAX_REPOS})",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub API token (default: GITHUB_TOKEN environment variable)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github-topic-recommender",
        description=(
            "Recommend relevant, established GitHub repository topics based on "
            "comparable repositories."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser(
        "analyze", help="analyze a GitHub repository (OWNER/REPOSITORY)"
    )
    analyze.add_argument("repository", help="repository as OWNER/REPOSITORY")
    _add_common_options(analyze)

    recommend = subparsers.add_parser(
        "recommend", help="recommend topics from a project description"
    )
    recommend.add_argument(
        "--description", required=True, help="free-text project description"
    )
    _add_common_options(recommend)

    explore = subparsers.add_parser(
        "explore", help="explore topics used within a niche"
    )
    explore.add_argument("niche", help='niche or field, e.g. "AI security"')
    _add_common_options(explore)

    return parser


def main(argv: list[str] | None = None, client: GitHubClient | None = None) -> int:
    args = build_parser().parse_args(argv)
    recommender = Recommender(client or GitHubClient(token=args.token))

    try:
        if args.command == "analyze":
            if "/" not in args.repository:
                print(
                    "error: expected OWNER/REPOSITORY (local paths are not "
                    "supported yet; use `recommend --description`)",
                    file=sys.stderr,
                )
                return 1
            owner, _, repo = args.repository.partition("/")
            report = recommender.analyze_repo(
                owner, repo, limit=args.limit, max_repos=args.max_repos
            )
        elif args.command == "recommend":
            report = recommender.recommend_from_description(
                args.description, limit=args.limit, max_repos=args.max_repos
            )
        else:
            report = recommender.explore(
                args.niche, limit=args.limit, max_repos=args.max_repos
            )
    except GitHubError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(render(report, args.format))
    return 0


if __name__ == "__main__":
    sys.exit(main())
