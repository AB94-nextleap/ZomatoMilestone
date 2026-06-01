"""Phase 4 parser tests: valid/invalid Groq-style JSON responses."""

from __future__ import annotations

import pytest

from src.llm.parser import LLMParseError, parse_llm_response


def test_parse_valid_json():
    raw = """
    {
      "summary": "Good options",
      "recommendations": [
        {"id": "r1", "rank": 1, "explanation": "Great match", "preference_matches": ["budget"]},
        {"id": "r2", "rank": 2, "explanation": "Good rating", "preference_matches": ["rating"]}
      ]
    }
    """
    parsed = parse_llm_response(raw)
    assert parsed.summary == "Good options"
    assert len(parsed.recommendations) == 2
    assert parsed.recommendations[0].id == "r1"


def test_parse_markdown_fenced_json():
    raw = """```json
    {"summary": null, "recommendations": [{"id":"r1","rank":1,"explanation":"ok"}]}
    ```"""
    parsed = parse_llm_response(raw)
    assert parsed.summary is None
    assert parsed.recommendations[0].id == "r1"


def test_parse_uses_restaurant_id_alias():
    raw = """
    {
      "recommendations": [
        {"restaurant_id":"abc", "rank":"1", "explanation":"ok"}
      ]
    }
    """
    parsed = parse_llm_response(raw)
    assert parsed.recommendations[0].id == "abc"
    assert parsed.recommendations[0].rank == 1


def test_parse_missing_recommendations_raises():
    raw = '{"summary":"x"}'
    with pytest.raises(LLMParseError):
        parse_llm_response(raw)


def test_parse_invalid_json_raises():
    raw = '{"recommendations":[{"id":"r1",}]}'
    with pytest.raises(LLMParseError):
        parse_llm_response(raw)
