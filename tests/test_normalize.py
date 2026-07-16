from collections import Counter

from github_topic_recommender.normalize import (
    JUNK_TOPICS,
    merge_variants,
    normalize_topic,
)


def test_normalize_lowercases_and_hyphenates():
    assert normalize_topic("  Secret Scanning ") == "secret-scanning"
    assert normalize_topic("supply_chain_security") == "supply-chain-security"


def test_normalize_strips_invalid_characters_and_hyphen_runs():
    assert normalize_topic("c++!") == "c"
    assert normalize_topic("--ci---cd--") == "ci-cd"
    assert normalize_topic("???") == ""


def test_normalize_applies_aliases():
    assert normalize_topic("AppSec") == "application-security"
    assert normalize_topic("k8s") == "kubernetes"


def test_junk_topics_include_common_noise():
    assert "hacktoberfest" in JUNK_TOPICS
    assert "awesome-list" in JUNK_TOPICS


def test_merge_variants_prefers_most_frequent_spelling():
    counts = Counter(
        {"developer-tools": 7, "developer-tool": 2, "devsecops": 5}
    )
    merged = merge_variants(counts)
    assert merged["developer-tools"] == (9, ["developer-tool"])
    assert merged["devsecops"] == (5, [])
    assert "developer-tool" not in merged


def test_merge_variants_does_not_merge_short_or_ss_words():
    counts = Counter({"sbom": 3, "css": 2})
    merged = merge_variants(counts)
    assert set(merged) == {"sbom", "css"}
