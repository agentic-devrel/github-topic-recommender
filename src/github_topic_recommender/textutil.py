"""Tokenization and keyword extraction for project text."""

from __future__ import annotations

import re
from collections import Counter

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-]*[a-z0-9]|[a-z0-9]", re.IGNORECASE)
_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITY_RE = re.compile(r"&[a-z]+;|&#\d+;")

STOPWORDS = frozenset(
    """
    a about above after again all also an and any are as at be because been
    before being below between both but by can could did do does doing down
    during each few for from further had has have having he her here hers him
    his how i if in into is it its itself just me more most my no nor not of
    off on once only or other our ours out over own same she should so some
    such than that the their theirs them then there these they this those
    through to too under until up very was we were what when where which while
    who whom why will with you your yours
    use used uses using via etc eg ie e.g i.e
    project repository repo repositories code source open-source opensource
    based support supports supported provide provides providing include
    includes including help helps make makes made new get one two like
    https http www com org net io href src img nbsp png svg jpg gif center
    github readme license documentation docs badge shield contributing
    install installation installing setup usage example examples quick start
    getting started guide overview features version release releases download
    downloads build status run running requirements contents table
    """.split()
)


def clean_text(text: str) -> str:
    """Strip markup that pollutes keyword extraction from READMEs."""
    text = _CODE_BLOCK_RE.sub(" ", text or "")
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _HTML_ENTITY_RE.sub(" ", text)
    return text


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens; hyphenated terms are kept whole."""
    return [match.group(0).lower() for match in _TOKEN_RE.finditer(text or "")]


def extract_keywords(text: str, limit: int = 20) -> list[str]:
    """Most frequent non-stopword tokens, ties broken by first occurrence."""
    tokens = tokenize(text)
    first_seen: dict[str, int] = {}
    counts: Counter[str] = Counter()
    for position, token in enumerate(tokens):
        if token in STOPWORDS or len(token) < 2 or token.isdigit():
            continue
        counts[token] += 1
        first_seen.setdefault(token, position)
    ranked = sorted(counts, key=lambda t: (-counts[t], first_seen[t]))
    return ranked[:limit]
