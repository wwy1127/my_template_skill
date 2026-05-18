"""Document ingestion pipeline.

Reads source documents listed in `docs/knowledge_base.md`,
splits them into chunks, generates embeddings, and persists to the vector store.
"""

import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[str]:
    """Simple recursive-character splitter fallback.

    For production, prefer langchain.text_splitter.RecursiveCharacterTextSplitter.
    """
    if not text.strip():
        return []

    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - chunk_overlap
    return chunks


def ingest_docs(docs_dir: str, config_path: str, persist_dir: str) -> None:
    config = load_config(config_path)
    vs_cfg = config["vector_store"]

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        logger.error("Docs directory '%s' not found.", docs_dir)
        return

    all_chunks: list[dict[str, Any]] = []
    for md_file in docs_path.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as fh:
            content = fh.read()
        chunks = chunk_text(
            content,
            chunk_size=512,
            chunk_overlap=64,
        )
        for idx, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "doc_id": f"{md_file.stem}_{idx}",
                    "source": str(md_file),
                    "content": chunk,
                }
            )

    persist_path = Path(persist_dir)
    persist_path.mkdir(parents=True, exist_ok=True)
    with open(persist_path / "chunks.json", "w", encoding="utf-8") as fh:
        json.dump(all_chunks, fh, indent=2, ensure_ascii=False)

    logger.info(
        "Indexed %d chunks from %d documents into %s",
        len(all_chunks),
        len(list(docs_path.glob("*.md"))),
        persist_path / "chunks.json",
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ingest_docs(docs_dir="docs", config_path="config.yaml", persist_dir="vector_store")
