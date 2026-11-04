import json
from pathlib import Path

import pytest

from tools.evaluation_runner.adapters import (
    AdapterRequestError,
    AdapterUnavailableError,
    GenerationRequest,
    MockAdapter,
)
from tools.evaluation_runner.runner import (
    DIMENSIONS,
    WEIGHTED_CATEGORIES,
    append_jsonl,
    main,
    parse_prompt_suite,
    read_weights,
)


ROOT = Path(__file__).resolve().parents[1]


def test_repository_prompt_suite_parses_all_stable_ids():
    suite = ROOT / "docs" / "evaluation" / "BIRAJ-PROMPT-SUITE-v0.1.md"
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

    assert set(weights) == set(WEIGHTED_CATEGORIES)
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["Hindi + Hinglish"] == pytest.approx(0.35)


def test_new_run_creates_unique_offline_run_without_model_server(tmp_path, capsys):
    result = main([
        "new-run",
        "--model-id",
        "local-candidate-not-selected",
        "--output-dir",
        str(tmp_path),
    ])
    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    run_dir = Path(payload["run_dir"])

    metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert metadata["mode"] == "offline-manual"
    assert metadata["model_revision"] == "unknown"
    assert metadata["runtime"] == "manual/offline"
    assert len(metadata["prompts"]) == 20
    assert (run_dir / "responses.jsonl").exists()
    assert (run_dir / "scorecards.jsonl").exists()


def test_report_keeps_runtime_metrics_separate_from_weighted_quality(tmp_path, capsys):
    assert main([
        "new-run",
        "--model-id",
        "test-candidate",
        "--output-dir",
        str(tmp_path),
    ]) == 0
    run_dir = Path(json.loads(capsys.readouterr().out)["run_dir"])
    metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))

    scores_by_category = dict(zip(WEIGHTED_CATEGORIES, (4, 3, 2, 1, 0)))
    for index, (category, score) in enumerate(scores_by_category.items(), start=1):
        prompt = next(item for item in metadata["prompts"] if item["category"] == category)
        append_jsonl(run_dir / "responses.jsonl", {
            "prompt_id": prompt["prompt_id"],
            "attempt": 1,
            "status": "completed",
            "metrics": {"ttft_ms": index * 100, "generation_tokens_per_sec": index * 2},
        })
        append_jsonl(run_dir / "scorecards.jsonl", {
            "prompt_id": prompt["prompt_id"],
            "attempt": 1,
            "scores": {dimension: score for dimension in DIMENSIONS},
        })

    assert main(["report", "--run-dir", str(run_dir)]) == 0
    capsys.readouterr()
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))

    weights = metadata["category_weights"]
    expected = sum(scores_by_category[name] * weights[name] for name in WEIGHTED_CATEGORIES)
    assert report["quality"]["status"] == "complete"
    assert report["quality"]["weighted_score_0_4"] == pytest.approx(expected)
    assert report["runtime_metrics"]["ttft_ms"]["median"] == pytest.approx(300)
    assert report["runtime_metrics"]["generation_tokens_per_sec"]["median"] == pytest.approx(6)
    assert report["quality"]["categories"]["Coding"]["mean_0_4"] == pytest.approx(3)


def test_report_marks_quality_incomplete_when_required_categories_are_missing(tmp_path, capsys):
    assert main([
        "new-run",
        "--model-id",
        "test-candidate",
        "--output-dir",
        str(tmp_path),
    ]) == 0
    run_dir = Path(json.loads(capsys.readouterr().out)["run_dir"])

    assert main(["report", "--run-dir", str(run_dir)]) == 0
    capsys.readouterr()
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))

    assert report["quality"]["status"] == "incomplete"
    assert report["quality"]["weighted_score_0_4"] is None
    assert len(report["quality"]["missing_categories"]) == 5


def test_mock_adapter_implements_provider_neutral_contract():
    adapter = MockAdapter(response_text="नमस्ते — mock response")
    request = GenerationRequest(
        prompt="हिंदी में नमस्ते कहो",
        system_prompt="तुम BIRAJ AI हो",
        temperature=0.2,
        max_new_tokens=64,
    )

    assert adapter.health() is True
    assert adapter.model_info()["runtime_name"] == "mock/offline"
    result = adapter.generate(request)

    assert result.text == "नमस्ते — mock response"
    assert result.model_id == "biraj-mock-model"
    assert result.runtime_name == "mock/offline"
    assert result.raw_metadata["mock"] is True
    assert adapter.requests == [request]


def test_mock_adapter_rejects_unavailable_runtime():
    adapter = MockAdapter(available=False)

    assert adapter.health() is False
    with pytest.raises(AdapterUnavailableError):
        adapter.generate(GenerationRequest(prompt="hello"))


@pytest.mark.parametrize("prompt", ["", "   ", "\n\t"])
def test_generation_request_rejects_empty_or_whitespace_prompt(prompt):
    with pytest.raises(AdapterRequestError, match="prompt must not be empty"):
        GenerationRequest(prompt=prompt)



@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("temperature", -0.01),
        ("temperature", 2.01),
        ("temperature", float("nan")),
        ("temperature", 10**1000),
        ("top_p", 0),
        ("top_p", 1.01),
        ("top_p", float("inf")),
        ("top_p", 10**1000),
        ("max_new_tokens", 0),
        ("max_new_tokens", 8193),
        ("max_new_tokens", 1.5),
    ],
)
def test_generation_request_rejects_invalid_generation_parameters(field, value):
    with pytest.raises(AdapterRequestError):
        GenerationRequest(prompt="hello", **{field: value})


def test_generation_request_accepts_parameter_boundaries():
    request = GenerationRequest(
        prompt="hello",
        temperature=0,
        top_p=1,
        max_new_tokens=8192,
    )

    assert request.temperature == 0
    assert request.top_p == 1
    assert request.max_new_tokens == 8192


def test_generation_request_rejects_prompt_and_system_prompt_over_limits():
    from tools.evaluation_runner.adapters import (
        MAX_PROMPT_CHARS,
        MAX_SYSTEM_PROMPT_CHARS,
    )

    with pytest.raises(AdapterRequestError, match="prompt exceeds maximum"):
        GenerationRequest(prompt="x" * (MAX_PROMPT_CHARS + 1))
    with pytest.raises(AdapterRequestError, match="system_prompt exceeds maximum"):
        GenerationRequest(
            prompt="hello",
            system_prompt="x" * (MAX_SYSTEM_PROMPT_CHARS + 1),
        )


def test_generation_request_rejects_invalid_stop_sequences():
    with pytest.raises(AdapterRequestError, match="stop sequence"):
        GenerationRequest(prompt="hello", stop=("",))
    with pytest.raises(AdapterRequestError, match="at most"):
        GenerationRequest(prompt="hello", stop=tuple(str(i) for i in range(17)))


def test_generation_request_metadata_is_recursively_immutable():
    source = {"labels": ["alpha"], "nested": {"enabled": True}}
    request = GenerationRequest(prompt="hello", metadata=source)

    source["labels"].append("changed")
    source["nested"]["enabled"] = False

    assert request.metadata["labels"] == ("alpha",)
    assert request.metadata["nested"]["enabled"] is True
    with pytest.raises(TypeError):
        request.metadata["new"] = "value"
    with pytest.raises(TypeError):
        request.metadata["nested"]["enabled"] = False


def test_generation_request_rejects_non_json_metadata():
    with pytest.raises(AdapterRequestError, match="JSON-compatible"):
        GenerationRequest(prompt="hello", metadata={"bad": object()})



def test_generation_request_uses_configurable_resource_limits():
    from tools.evaluation_runner.adapters import GenerationLimits

    limits = GenerationLimits(
        max_prompt_chars=5,
        max_system_prompt_chars=4,
        max_new_tokens=3,
        max_stop_sequences=1,
        max_stop_sequence_chars=2,
    )
    request = GenerationRequest(
        prompt="hello",
        system_prompt="safe",
        max_new_tokens=3,
        stop=("OK",),
        limits=limits,
    )
    assert request.limits is limits

    with pytest.raises(AdapterRequestError, match="prompt exceeds maximum length of 5"):
        GenerationRequest(prompt="123456", limits=limits)
    with pytest.raises(AdapterRequestError, match="system_prompt exceeds maximum length of 4"):
        GenerationRequest(prompt="ok", system_prompt="12345", limits=limits)
    with pytest.raises(AdapterRequestError, match="max_new_tokens must be an integer between 1 and 3"):
        GenerationRequest(prompt="ok", max_new_tokens=4, limits=limits)
    with pytest.raises(AdapterRequestError, match="at most 1 sequences"):
        GenerationRequest(prompt="ok", stop=("A", "B"), limits=limits)
    with pytest.raises(AdapterRequestError, match="at most 2 characters"):
        GenerationRequest(prompt="ok", stop=("END",), limits=limits)


@pytest.mark.parametrize("field", [
    "max_prompt_chars",
    "max_system_prompt_chars",
    "max_new_tokens",
    "max_stop_sequences",
    "max_stop_sequence_chars",
])
@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_generation_limits_reject_non_positive_or_non_integer_values(field, value):
    from tools.evaluation_runner.adapters import GenerationLimits

    with pytest.raises(AdapterRequestError, match="positive integer"):
        GenerationLimits(**{field: value})


def test_record_score_rejects_duplicate_prompt_attempt_without_overwriting_evidence(tmp_path, capsys):
    assert main([
        "new-run",
        "--model-id",
        "test-candidate",
        "--output-dir",
        str(tmp_path),
    ]) == 0
    run_dir = Path(json.loads(capsys.readouterr().out)["run_dir"])

    assert main([
        "record-response",
        "--run-dir", str(run_dir),
        "--prompt-id", "HI-01",
        "--response", "नमस्ते",
    ]) == 0
    capsys.readouterr()

    score_file = tmp_path / "score.json"
    score_file.write_text(json.dumps({"language_0_4": 4}), encoding="utf-8")
    command = [
        "record-score",
        "--run-dir", str(run_dir),
        "--prompt-id", "HI-01",
        "--attempt", "1",
        "--scorecard-file", str(score_file),
    ]
    assert main(command) == 0
    capsys.readouterr()
    original = (run_dir / "scorecards.jsonl").read_text(encoding="utf-8")

    assert main(command) == 2
    assert "already exists" in capsys.readouterr().err
    assert (run_dir / "scorecards.jsonl").read_text(encoding="utf-8") == original
    assert len(original.splitlines()) == 1


def test_record_response_preserves_failed_and_skipped_attempts(tmp_path, capsys):
    assert main([
        "new-run",
        "--model-id",
        "test-candidate",
        "--output-dir",
        str(tmp_path),
    ]) == 0
    run_dir = Path(json.loads(capsys.readouterr().out)["run_dir"])

    for status, note in (("failed", "runtime unavailable"), ("skipped", "manual skip")):
        assert main([
            "record-response",
            "--run-dir", str(run_dir),
            "--prompt-id", "HI-01",
            "--status", status,
            "--failure-note", note,
        ]) == 0
        capsys.readouterr()

    records = [
        json.loads(line)
        for line in (run_dir / "responses.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [(item["attempt"], item["status"]) for item in records] == [
        (1, "failed"),
        (2, "skipped"),
    ]
    assert all(item["response_text"] is None for item in records)
    assert [item["failure_note"] for item in records] == [
        "runtime unavailable",
        "manual skip",
    ]
