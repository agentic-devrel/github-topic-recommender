from github_topic_recommender.textutil import clean_text, extract_keywords, tokenize


def test_clean_text_strips_markup_and_urls():
    raw = (
        "# Scanner <img src='logo.png'>&nbsp;\n"
        "See https://example.com/docs for details.\n"
        "```bash\npip install scanner\n```\n"
        "Run `scanner --help` to scan secrets."
    )
    cleaned = clean_text(raw)
    assert "https" not in cleaned
    assert "img" not in cleaned
    assert "nbsp" not in cleaned
    assert "pip install" not in cleaned
    assert "secrets" in cleaned


def test_tokenize_keeps_hyphenated_terms():
    assert tokenize("A CI/CD supply-chain scanner") == [
        "a",
        "ci",
        "cd",
        "supply-chain",
        "scanner",
    ]


def test_extract_keywords_ranks_by_frequency_then_position():
    text = "scanner scans secrets. The scanner also scans dependencies for secrets."
    keywords = extract_keywords(text)
    assert keywords[0] == "scanner"
    assert keywords.index("secrets") < keywords.index("dependencies")


def test_extract_keywords_drops_stopwords_and_digits():
    keywords = extract_keywords("the a 2024 open-source project using security")
    assert "the" not in keywords
    assert "2024" not in keywords
    assert "project" not in keywords  # domain filler stopword
    assert "security" in keywords


def test_extract_keywords_respects_limit():
    text = " ".join(f"word{i}" for i in range(50))
    assert len(extract_keywords(text, limit=5)) == 5
