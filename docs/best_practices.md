# Best Practices

## Prompt Engineering

### Structure
1. **Role** — who the model is.
2. **Context** — what background information it has.
3. **Task** — what it must do.
4. **Format** — exactly how output should look.
5. **Guardrails** — boundaries it must not cross.

### Few-Shot Examples
- Provide 2–3 input/output pairs for complex tasks.
- Keep examples semantically close to the expected production input.
- Update examples when the skill domain evolves.

### Hallucination Mitigation
- Explicitly instruct: _"If you don't know, say `NEED_MORE_INFO`"_.
- Require `sources` array populated from retrieved context.
- Set `confidence` below 0.7 when context is insufficient.
- Run evaluator on every output before production use.

## RAG Optimization

### Chunking Strategy
- Prefer **semantic chunking** over fixed-size for narrative documents.
- Use **recursive character splitting** for code / structured text.
- Keep chunks between 256–1024 tokens depending on embedding model limits.

### Retrieval Tuning
- **Top-K**: Start at 5, increase if answers are incomplete.
- **Similarity threshold**: 0.75 is a safe default; lower for broad domains.
- Re-rank retrieved chunks with a cross-encoder for critical accuracy.

### Index Maintenance
- Re-index when source documents change.
- Version your vector store alongside your code.
- Run retrieval tests as part of CI.

## Evaluation

### Metrics to Track
- **Pass rate** — % of test cases scoring `PASS`.
- **Confidence correlation** — does high self-confidence match evaluator score?
- **Latency p50 / p95 / p99** — track over time to catch regressions.

### Continuous Improvement
1. Collect production `WARN` / `FAIL` outputs.
2. Analyse failure patterns.
3. Update prompts, context, or few-shot examples.
4. Re-run regression suite.
5. Deploy only when pass rate returns to baseline.

## Security

- Never log raw user input or model output containing PII.
- Sanitise all inputs before embedding or prompt injection.
- Rotate API keys regularly; use `.env` and never commit secrets.
- Rate-limit production endpoints to prevent abuse.
