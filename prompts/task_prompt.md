# Task Prompt

You are given the following task by the user:

<task>
{{USER_TASK}}
</task>

{% if CONTEXT %}
Use the following retrieved context to inform your answer:

<context>
{{CONTEXT}}
</context>
{% endif %}

{% if FEW_SHOT_EXAMPLES %}
Refer to these examples for expected behaviour:

<examples>
{{FEW_SHOT_EXAMPLES}}
</examples>
{% endif %}

## Instructions

1. Analyse the task carefully.
2. {% if CONTEXT %}Prioritise information from `<context>` over your training data.{% else %}Rely on your training data.{% endif %}
3. Produce output in the format defined in your system prompt.
4. Set `confidence` based on how certain you are:
   - `1.0` — confirmed by context / training data.
   - `0.7 – 0.9` — likely correct but some ambiguity.
   - `0.4 – 0.6` — speculative; needs human review.
   - `≤ 0.3` — guess; DO NOT use in production.
5. Include `sources` array with IDs of all documents you referenced.
6. Populate `trace` with:
   - `"latency_ms": <your processing time estimate>`
   - `"context_docs_used": <count of context documents referenced>`

{% if CONSTRAINTS %}
## Additional Constraints
{{CONSTRAINTS}}
{% endif %}

Now complete the task.
