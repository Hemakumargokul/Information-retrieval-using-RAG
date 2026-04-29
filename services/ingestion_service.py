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
_CACHE_DIR = "ingestion_cache"

def _tag_content_type(node):
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
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=1000, chunk_overlap=200),
            OpenAIEmbedding(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY),
        ]
    )
    if os.path.exists(os.path.join(_CACHE_DIR, "llama_cache")):
        pipeline.load(persist_dir=_CACHE_DIR)
    return pipeline

@lru_cache(maxsize=None)
def get_pipeline_v2() -> IngestionPipeline:
    return IngestionPipeline(
        transformations=[
            MarkdownNodeParser(),
            OpenAIEmbedding(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY),
        ]
    )

def _ingest_v1(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline) -> int:
    from llama_index.core import SimpleDirectoryReader
    docs = SimpleDirectoryReader(directory, required_exts=[".pdf"], recursive=True).load_data()
    logger.info("v1: Loaded %d documents", len(docs))
    nodes = pipeline.run(documents=docs)
    pipeline.cache.persist(_CACHE_DIR)
    logger.info("v1: Pipeline produced %d nodes", len(nodes))
    texts_and_embeddings = [(n.get_content(), n.embedding) for n in nodes if n.embedding]
    metadatas = [n.metadata for n in nodes if n.embedding]
    vector_store.add_embeddings(texts_and_embeddings, metadatas)
    return len(texts_and_embeddings)

def _ingest_v2(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline) -> int:
    docs = []
    for path in Path(directory).rglob("*.pdf"):
        md = pymupdf4llm.to_markdown(str(path))
        docs.append(Document(text=md, metadata={"file_path": str(path)}))
    if not docs:
        raise ValueError(f"No PDF files found in {directory}.")
    logger.info("v2: Loaded %d PDFs as markdown", len(docs))
    nodes = pipeline.run(documents=docs)
    logger.info("v2: Pipeline produced %d nodes", len(nodes))
    nodes = [_tag_content_type(n) for n in nodes if n.embedding]
    texts_and_embeddings = [(n.get_content(), n.embedding) for n in nodes]
    metadatas = [n.metadata for n in nodes]
    vector_store.add_embeddings(texts_and_embeddings, metadatas)
    return len(nodes)

def ingest(directory: str, vector_store: BaseVectorStore, pipeline: IngestionPipeline, strategy: str) -> int:
    if strategy == "v2":
        return _ingest_v2(directory, vector_store, pipeline)
    return _ingest_v1(directory, vector_store, pipeline)
