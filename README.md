# AI Skill Engineering Template

A reusable, plug-and-play template for building production-grade AI skills (agents, RAG pipelines, evaluator loops).  
Follows the coding standards defined in `opencode.md`.

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
python scripts/ingest_docs.py
python scripts/run_skill.py --task "your task here"
python scripts/evaluate_output.py
```

## Directory Layout

| Path                  | Purpose                                         |
|-----------------------|-------------------------------------------------|
| `SPEC.md`             | Skill specification (I/O, behaviour, constraints) |
| `RULES.md`            | Coding rules inherited from `opencode.md`       |
| `config.yaml`         | Run-time parameters (model, temperature, top-k) |
| `.env.example`        | Environment variable template                   |
| `prompts/`            | System / task / evaluator prompt templates      |
| `docs/`               | Knowledge base, best practices, domain glossary |
| `scripts/`            | Execution, ingestion, evaluation, deployment    |
| `tests/`              | Test cases, expected outputs, regression suite  |
| `outputs/`            | Skill run results (.json + .md)                 |
| `vector_store/`       | Persisted vector embeddings (gitignored)        |

## Conventions

- TypeScript (not) – this template is Python-first; type hints are mandatory.
- All prompts use Jinja2 `{{placeholder}}` syntax.
- Output is always written to `outputs/<skill_name>/<iso_datetime>/`.
- Evaluation runs against `tests/expected_outputs.md` and reports a pass/fail delta.
