"""Retrieval-augmented generation: fetch relevant context and answer with an LLM."""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from services.vector_store.base import BaseVectorStore

logger = logging.getLogger(__name__)

# System prompt that grounds the model in the retrieved context and forces it to
# self-report how well that context covers the question (the "Context Quality" section).
_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the question using only the provided context.

After your answer, always include a "Context Quality" section using this format:

Context Quality:
- Summary: <one sentence describing what the retrieved context covers>
- Relevance: <High | Medium | Low> — <brief reason>
- If relevance is Medium or Low: What was missing: <what information would have been needed to answer better>

If the context is completely empty or irrelevant, respond with "I don't have enough information to answer that." and still fill in the Context Quality section.

Context:
{context}

Question: {question}

Answer:""")

async def ask(question: str, llm: BaseChatModel, vector_store: BaseVectorStore, strategy: str = "v1") -> str:
    """Answer ``question`` using context retrieved from ``vector_store``.

    ``strategy`` selects the retrieval approach:
      * ``v1`` – pure semantic search over the FAISS vector index.
      * ``v2`` – hybrid search combining FAISS (semantic) with BM25 (keyword),
        which improves recall for exact terms that embeddings tend to miss.
    """
    if strategy == "v2":
        all_docs = vector_store.get_all_documents()
        faiss_retriever = vector_store.get_retriever(score_threshold=0.0)
        if all_docs:
            # BM25 needs the raw documents in memory; blend it with FAISS so
            # semantic matches are weighted higher (0.6) than keyword matches (0.4).
            bm25_retriever = BM25Retriever.from_documents(all_docs, k=5)
            retriever = EnsembleRetriever(
                retrievers=[faiss_retriever, bm25_retriever],
                weights=[0.6, 0.4]
            )
        else:
            # Nothing ingested yet – fall back to FAISS alone.
            retriever = faiss_retriever
        logger.info("v2: using hybrid retriever")
    else:
        retriever = vector_store.get_retriever(score_threshold=0.0)
        logger.info("v1: using FAISS retriever")

    # Retrieve the relevant chunks and concatenate them into a single context blob.
    docs = await retriever.ainvoke(question)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    logger.info("Retrieved %d chunks (strategy=%s)\nContext:\n%s", len(docs), strategy, context)

    # Render the grounded prompt and stream it through the LLM to a plain string.
    prompt_value = _PROMPT.invoke({"context": context, "question": question})
    return await (llm | StrOutputParser()).ainvoke(prompt_value)
