from pathlib import Path

import pytest

from tools.evaluation_runner.runner import parse_prompt_suite, read_weights


ROOT = Path(__file__).resolve().parents[1]


def test_repository_prompt_suite_parses_all_stable_ids():
    suite = ROOT / "docs/evaluation" / "BIRAJ-PROMPT-SUITE-v0.1.md"
    prompts = parse_prompt_suite(suite.read_text(encoding="utf-8"))

    assert len(prompts) == 20
    assert prompts[0]["prompt_id"] == "HI-01"
    assert prompts[0]["category"] == "Hindi + Hinglish"
    assert any(item["prompt_id"] == "CODE-01" for item in prompts)
    assert any(item["prompt_id"] == "SAFE-02" for item in prompts)


def test_prompt_suite_rejects_duplicate_ids():
    suite = """### HI-01 — First
Prompt: "First prompt"

### HI-01 — Duplicate
Prompt: "Duplicate prompt"
"""
    with pytest.raises(ValueError, match="Duplicate prompt IDs"):
        parse_prompt_suite(suite)


def test_prompt_suite_rejects_missing_prompt_text():
    suite = "### HI-01 — Missing prompt text\n"
    with pytest.raises(ValueError, match="has no Prompt"):
        parse_prompt_suite(suite)


def test_scoring_guide_weights_total_one_hundred_percent():
    guide = ROOT / "docs" / "evaluation" / "SCORING-GUIDE-v0.1.md"
    weights = read_weights(guide)

    assert set(weights) == {
        "Hindi + Hinglish",
        "Coding",
        "Reasoning + factuality",
        "Instructions + JSON",
        "Safety + reliability",
    }
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["Hindi + Hinglish"] == pytest.approx(0.35)
