# Coding Rules

This project inherits all rules from the root `opencode.md`.  
The following skill-specific additions apply.

## Prompt Engineering Rules

### Do
- Start with a clear role assignment.
- Define output format with concrete examples.
- Use few-shot examples when ambiguity is high.
- Constrain the model with guardrails (e.g., "If unsure, respond with `NEED_MORE_INFO`").

### Don't
- Include sensitive data in prompts.
- Rely on implicit knowledge the model may not have.
- Use open-ended instructions without boundaries.

## Evaluation Rules

### Pass Criteria
- Output format matches `SPEC.md` contract.
- `confidence` ≥ 0.7 for production flows.
- No hallucinated references (sources MUST exist in vector store).
- Latency ≤ threshold defined in `config.yaml`.

### Regressions
- Any previously passing test case that now fails is a blocking regression.
- Run `tests/regression_suite.py` before every deployment.

## File Conventions

- Python: PEP 8, type hints, max 300 lines per module.
- YAML: 2-space indent, no tabs.
- Markdown: one H1 per file, blank line before/after headings.
- Templates: Jinja2 `{{ }}</% %>` only; no raw Python code blocks.
