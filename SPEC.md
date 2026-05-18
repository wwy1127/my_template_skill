# Skill Specification

## Identity

| Field           | Value                        |
|-----------------|------------------------------|
| **Skill Name**  | `{{SKILL_NAME}}`             |
| **Version**     | `{{SKILL_VERSION}}`          |
| **Author**      | `{{AUTHOR}}`                 |
| **License**     | `{{LICENSE}}`                |

## Behaviour Contract

### Input

| Parameter     | Type     | Required | Description                       |
|---------------|----------|----------|-----------------------------------|
| `task`        | `string` | yes      | Natural-language task description |
| `context`     | `string` | no       | Additional domain context         |
| `format`      | `enum`   | no       | `json` / `markdown` / `text`      |
| `options`     | `dict`   | no       | Extra key-value overrides         |

### Output

| Field        | Type     | Description                           |
|--------------|----------|---------------------------------------|
| `result`     | `string` | Primary output in requested format    |
| `confidence` | `float`  | Self-reported confidence 0.0 – 1.0    |
| `sources`    | `list`   | Referenced document IDs (if RAG used) |
| `trace`      | `dict`   | Execution metadata (latency, tokens)  |

### Constraints

1. Output MUST respect the requested `format`.
2. `confidence` ≤ 0.6 MUST trigger an evaluator re-prompt.
3. All user input is treated as untrusted; run through sanitisation.
4. PII / secrets MUST NOT appear in logs or outputs.

## Integration Points

| Integration        | Purpose                         |
|--------------------|---------------------------------|
| `scripts/run_skill.py` | Primary execution entrypoint |
| `prompts/system_prompt.md` | System-level instructions |
| `docs/knowledge_base.md` | RAG retrieval source      |
| `scripts/evaluate_output.py` | Quality gate          |
