import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from services.vector_store.base import BaseVectorStore

logger = logging.getLogger(__name__)

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
    if strategy == "v2":
        all_docs = vector_store.get_all_documents()
        faiss_retriever = vector_store.get_retriever(score_threshold=0.0)
        if all_docs:
            bm25_retriever = BM25Retriever.from_documents(all_docs, k=5)
            retriever = EnsembleRetriever(
                retrievers=[faiss_retriever, bm25_retriever],
                weights=[0.6, 0.4]
            )
        else:
            retriever = faiss_retriever
        logger.info("v2: using hybrid retriever")
    else:
        retriever = vector_store.get_retriever(score_threshold=0.0)
        logger.info("v1: using FAISS retriever")

    docs = await retriever.ainvoke(question)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    logger.info("Retrieved %d chunks (strategy=%s)\nContext:\n%s", len(docs), strategy, context)

    prompt_value = _PROMPT.invoke({"context": context, "question": question})
    return await (llm | StrOutputParser()).ainvoke(prompt_value)
