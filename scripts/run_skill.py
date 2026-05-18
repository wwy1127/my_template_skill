"""Core execution entrypoint for an AI skill.

Loads config, assembles the prompt from templates, invokes the LLM,
and persists output to `outputs/<skill_name>/<iso_datetime>/`.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from openai import OpenAI

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_template(env: Environment, name: str) -> str:
    try:
        return env.get_template(name).render()
    except TemplateNotFound:
        logger.error("Template '%s' not found in prompts/", name)
        sys.exit(1)


def build_prompt(
    system_template: str,
    task_template: str,
    task: str,
    context: Optional[str],
    few_shot: Optional[str],
    constraints: Optional[str],
    skill_name: str,
    skill_domain: str,
    role_description: str,
) -> dict[str, str]:
    env = Environment(loader=FileSystemLoader("."))
    system_text = env.from_string(system_template).render(
        SKILL_NAME=skill_name,
        SKILL_DOMAIN=skill_domain,
        ROLE_DESCRIPTION=role_description,
    )
    task_text = env.from_string(task_template).render(
        USER_TASK=task,
        CONTEXT=context,
        FEW_SHOT_EXAMPLES=few_shot,
        CONSTRAINTS=constraints,
    )
    return {"system": system_text, "user": task_text}


def call_llm(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"result": content, "confidence": 0.0, "sources": [], "trace": {}}
    return parsed


def persist_output(
    base_dir: str,
    skill_name: str,
    output: dict[str, Any],
    formats: list[str],
) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(base_dir) / skill_name / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        if fmt == "json":
            with open(out_dir / "output.json", "w", encoding="utf-8") as fh:
                json.dump(output, fh, indent=2, ensure_ascii=False)
        elif fmt == "markdown":
            with open(out_dir / "output.md", "w", encoding="utf-8") as fh:
                fh.write(f"# Output\n\n{output.get('result', '')}\n")
                fh.write(f"\n**Confidence**: {output.get('confidence', 0)}\n")
                fh.write(f"\n**Sources**: {output.get('sources', [])}\n")

    logger.info("Output persisted to %s", out_dir)


def run(config_path: str, task: str, context: Optional[str] = None) -> None:
    config = load_config(config_path)

    llm_cfg = config["llm"]
    runtime_cfg = config["runtime"]
    output_cfg = config["output"]
    skill_cfg = config["skill"]

    logging.basicConfig(
        level=getattr(logging, runtime_cfg.get("log_level", "INFO")),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    with (
        open("prompts/system_prompt.md", "r", encoding="utf-8") as sf,
        open("prompts/task_prompt.md", "r", encoding="utf-8") as tf,
    ):
        system_template = sf.read()
        task_template = tf.read()

    prompt = build_prompt(
        system_template=system_template,
        task_template=task_template,
        task=task,
        context=context,
        few_shot=None,
        constraints=None,
        skill_name=skill_cfg.get("name", "unknown"),
        skill_domain=skill_cfg.get("domain", "general"),
        role_description=skill_cfg.get("role_description", ""),
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"]},
    ]

    for attempt in range(1, runtime_cfg.get("max_retries", 1) + 1):
        try:
            output = call_llm(
                client=client,
                model=llm_cfg["model"],
                messages=messages,
                temperature=llm_cfg.get("temperature", 0.3),
                max_tokens=llm_cfg.get("max_tokens", 4096),
                timeout=llm_cfg.get("timeout_seconds", 120),
            )
            persist_output(
                base_dir=output_cfg.get("base_dir", "outputs/"),
                skill_name=skill_cfg.get("name", "unknown"),
                output=output,
                formats=output_cfg.get("formats", ["json"]),
            )
            return
        except Exception as exc:
            logger.warning("Attempt %d failed: %s", attempt, exc)
            if attempt == runtime_cfg.get("max_retries", 1):
                logger.error("All retries exhausted.")
                raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run an AI skill")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--context", help="Optional context string")
    args = parser.parse_args()
    run(config_path=args.config, task=args.task, context=args.context)
