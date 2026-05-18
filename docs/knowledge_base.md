# Knowledge Base

This document serves as the **RAG ingestion manifest**.
List every document, URL, or raw text block that should be embedded and stored in `vector_store/`.

## Document Index

| Doc ID                     | Path / URL                    | Description                  | Chunk Size | Overlap |
|----------------------------|-------------------------------|------------------------------|------------|---------|
| `{{DOC_ID_01}}`            | `docs/domain_reference.md`    | Domain glossary & rules      | 512        | 64      |
| `{{DOC_ID_02}}`            | `docs/best_practices.md`      | Prompt & RAG best practices  | 512        | 64      |
| `{{ADD_CUSTOM_DOCS_HERE}}` |                               |                              |            |         |

## Ingestion Pipeline

```text
Raw Doc → Text Splitter (RecursiveCharacter) → Embedding Model → Vector Store
```

### Parameters (from `config.yaml`)

- **Chunk size**: 512 tokens
- **Chunk overlap**: 64 tokens
- **Embedding model**: `text-embedding-3-small`
- **Top-K retrieval**: 5 documents
- **Similarity threshold**: 0.75

## Adding New Documents

1. Add a row to the **Document Index** table above.
2. Place the source file in `docs/` or add the URL.
3. Run `python scripts/ingest_docs.py` to re-index.
4. Verify retrieval with `python scripts/evaluate_output.py`.
