"""Document ingestion: load PDFs, chunk and embed them, and store the vectors.

Two ingestion strategies are supported (see :func:`ingest`):
  * ``v1`` – sentence-based fixed-size chunking of the raw PDF text.
  * ``v2`` – convert each PDF to Markdown first, then chunk along its structure.
"""
import os
import logging
from pathlib import Path
from functools import lru_cache

import pymupdf4llm
from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter, MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

from services.vector_store.base import BaseVectorStore
from config import settings

logger = logging.getLogger(__name__)
# Directory where the v1 pipeline persists its transformation cache between runs.
_CACHE_DIR = "ingestion_cache"

def _tag_content_type(node):
    """Heuristically label a chunk as code, table, or prose for later filtering.

    Uses cheap text signals: fenced/indented blocks look like code, and lots of
    pipe characters look like a Markdown table; everything else is prose.
    """
    text = node.get_content()
    if "```" in text or "\n    " in text[:200]:
        node.metadata["content_type"] = "code"
    elif text.count("|") > 3:
        node.metadata["content_type"] = "table"
    else:
        node.metadata["content_type"] = "prose"
    return node

@lru_cache(maxsize=None)
def get_pipeline_v1() -> IngestionPipeline:
    """Build (and memoize) the v1 pipeline: fixed-size sentence chunks + embeddings."""
    pipeline = IngestionPipeline(
        transformations=[
            # ~1000-char chunks with 200-char overlap so context isn't lost at boundaries.
            SentenceSplitter(chunk_size=1000, chunk_overlap=200),
            OpenAIEmbedding(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY),
        ]
    )
    # Reuse previously computed chunks/embeddings if a cache exists on disk.
    if os.path.exists(os.path.join(_CACHE_DIR, "llama_cache")):
        pipeline.load(persist_dir=_CACHE_DIR)
    return pipeline

@lru_cache(maxsize=None)
def get_pipeline_v2() -> IngestionPipeline:
    """Build (and memoize) the v2 pipeline: Markdown-structure chunking + embeddings."""
    return IngestionPipeline(
        transformations=[
            # Split along Markdown headings/sections instead of a fixed character count.
            MarkdownNodeParser(),
            OpenAIEmbedding(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY),
        ]
    )

def _ingest_v1(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline) -> int:
    from llama_index.core import SimpleDirectoryReader
    # Recursively load every PDF under the directory as raw text documents.
    docs = SimpleDirectoryReader(directory, required_exts=[".pdf"], recursive=True).load_data()
    logger.info("v1: Loaded %d documents", len(docs))
    nodes = pipeline.run(documents=docs)
    # Persist the cache so re-ingesting the same content skips the embedding cost.
    pipeline.cache.persist(_CACHE_DIR)
    logger.info("v1: Pipeline produced %d nodes", len(nodes))
    # Only keep nodes that were successfully embedded before writing to the store.
    texts_and_embeddings = [(n.get_content(), n.embedding) for n in nodes if n.embedding]
    metadatas = [n.metadata for n in nodes if n.embedding]
    vector_store.add_embeddings(texts_and_embeddings, metadatas)
    return len(texts_and_embeddings)

def _ingest_v2(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline) -> int:
    docs = []
    # Convert each PDF to Markdown so the pipeline can chunk along document structure.
    for path in Path(directory).rglob("*.pdf"):
        md = pymupdf4llm.to_markdown(str(path))
        docs.append(Document(text=md, metadata={"file_path": str(path)}))
    if not docs:
        raise ValueError(f"No PDF files found in {directory}.")
    logger.info("v2: Loaded %d PDFs as markdown", len(docs))
    nodes = pipeline.run(documents=docs)
    logger.info("v2: Pipeline produced %d nodes", len(nodes))
    # Keep only embedded nodes and annotate each with its content type.
    nodes = [_tag_content_type(n) for n in nodes if n.embedding]
    texts_and_embeddings = [(n.get_content(), n.embedding) for n in nodes]
    metadatas = [n.metadata for n in nodes]
    vector_store.add_embeddings(texts_and_embeddings, metadatas)
    return len(nodes)

def ingest(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline, strategy: str) -> int:
    """Ingest all PDFs in ``directory`` using the given ``strategy`` (``v1`` or ``v2``).

    Returns the number of chunks written to the vector store.
    """
    if strategy == "v2":
        return _ingest_v2(directory, vector_store, pipeline)
    return _ingest_v1(directory, vector_store, pipeline)
