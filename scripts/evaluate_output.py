"""Output evaluator script.

Compares actual skill outputs against expected outputs using the evaluator prompt.
Generates a pass/fail report written to `outputs/evaluation_report.json`.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI

logger = logging.getLogger(__name__)


def load_expected(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_actual(output_dir: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    base = Path(output_dir)
    for json_file in base.rglob("output.json"):
        with open(json_file, "r", encoding="utf-8") as fh:
            results.append({"path": str(json_file.parent), "output": json.load(fh)})
    return results


def evaluate(
    actual: dict[str, Any],
    expected: dict[str, Any],
    client: OpenAI,
    model: str,
) -> dict[str, Any]:
    with open("prompts/evaluator_prompt.md", "r", encoding="utf-8") as fh:
        evaluator_template = fh.read()

    prompt_text = evaluator_template.replace("{{ACTUAL_OUTPUT}}", json.dumps(actual))
    prompt_text = prompt_text.replace("{{EXPECTED_OUTPUT}}", json.dumps(expected))
    prompt_text = prompt_text.replace("{{TEST_CASE_ID}}", expected.get("test_case_id", "unknown"))
    prompt_text = prompt_text.replace(
        "{{TEST_CASE_DESCRIPTION}}", expected.get("description", "")
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.0,
        max_tokens=1024,
    )
    content = response.choices[0].message.content or ""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"verdict": "FAIL", "scores": {}, "summary": "Parse error", "suggestions": []}


def run(expected_path: str, output_dir: str, config_path: str) -> None:
    config = load_config(config_path)
    expected = load_expected(expected_path)
    actuals = load_actual(output_dir)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    report: list[dict[str, Any]] = []
    for entry in actuals:
        eval_result = evaluate(
            actual=entry["output"],
            expected=expected,
            client=client,
            model=config["llm"]["model"],
        )
        report.append(
            {
                "output_path": entry["path"],
                "verdict": eval_result.get("verdict"),
                "scores": eval_result.get("scores"),
                "summary": eval_result.get("summary"),
                "suggestions": eval_result.get("suggestions"),
            }
        )

    report_path = Path(output_dir) / "evaluation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    passes = sum(1 for r in report if r["verdict"] == "PASS")
    failures = sum(1 for r in report if r["verdict"] != "PASS")
    logger.info("Evaluation complete: %d pass, %d fail. Report saved to %s", passes, failures, report_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    run(
        expected_path="tests/expected_outputs.json",
        output_dir="outputs/",
        config_path="config.yaml",
    )
