from src.filtering import find_terms, keyword_filter, normalize_text


def test_normalize_text_lowercases_and_collapses_spaces():
    assert normalize_text("  Codex   RESET\nSoon ") == "codex reset soon"


def test_find_terms_matches_phrases_case_insensitively():
    text = "I will reset everyone's Codex usage limits."
    assert find_terms(text, ["reset", "usage limits", "quota"]) == ["reset", "usage limits"]


def test_keyword_filter_accepts_reset_related_codex_post():
    result = keyword_filter(
        "I'll reset everyone's Codex usage today.",
        any_terms=["reset", "codex", "usage"],
        required_any=["codex", "usage"],
    )
    assert result.matched
    assert result.matched_terms == ["reset", "codex", "usage"]


def test_keyword_filter_rejects_unrelated_keyword_without_required_context():
    result = keyword_filter(
        "The bank reset my card PIN.",
        any_terms=["reset", "bank"],
        required_any=["codex", "usage"],
    )
    assert not result.matched
    assert result.matched_terms == ["reset", "bank"]


def test_keyword_filter_rejects_text_without_keywords():
    result = keyword_filter(
        "A normal product update shipped today.",
        any_terms=["reset", "codex"],
        required_any=["codex"],
    )
    assert not result.matched
    assert result.matched_terms == []
