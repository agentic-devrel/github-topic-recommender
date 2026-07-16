"""Render a recommendation Report as text, JSON, or Markdown."""

from __future__ import annotations

import json
from dataclasses import asdict

from .models import Report

FORMATS = ("text", "json", "markdown")


def render(report: Report, fmt: str = "text") -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "markdown":
        return render_markdown(report)
    if fmt == "text":
        return render_text(report)
    raise ValueError(f"Unknown format: {fmt!r} (expected one of {FORMATS})")


def render_json(report: Report) -> str:
    return json.dumps(asdict(report), indent=2)


def _sample_line(report: Report) -> str:
    sample = report.sample
    return (
        f"{sample['repositories_analyzed']} repositories analyzed, "
        f"{sample['repositories_with_topics']} with topics, "
        f"{sample['active_repositories']} active in the last year"
    )


def render_text(report: Report) -> str:
    lines = [
        f"Topic recommendations for {report.project['name']}",
        f"Sample: {_sample_line(report)}",
        "",
    ]
    if not report.recommendations:
        lines.append("No topics could be recommended from the sample.")
    else:
        width = max(len(r.topic) for r in report.recommendations)
        for rec in report.recommendations:
            lines.append(
                f"  {rec.topic:<{width}}  score {rec.score:.2f}  "
                f"[{rec.role}]  {rec.reason}"
            )
    lines.append("")
    lines.append("Notes:")
    lines.extend(f"  - {note}" for note in report.notes)
    return "\n".join(lines)


def render_markdown(report: Report) -> str:
    lines = [
        f"# Topic recommendations for `{report.project['name']}`",
        "",
        f"Sample: {_sample_line(report)}.",
        "",
        "| Topic | Score | Role | Prevalence | Why it fits |",
        "|---|---|---|---|---|",
    ]
    for rec in report.recommendations:
        lines.append(
            f"| `{rec.topic}` | {rec.score:.2f} | {rec.role} "
            f"| {rec.niche_prevalence:.0%} | {rec.reason} |"
        )
    lines.append("")
    lines.extend(f"> {note}" for note in report.notes)
    return "\n".join(lines)
