import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from services.vector_store.base import BaseVectorStore

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the question using only the provided context.
If the context does not contain enough information to answer, respond with "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:""")

async def ask(question: str, llm: BaseChatModel, vector_store: BaseVectorStore) -> str:
    retriever = vector_store.get_retriever()
    docs = await retriever.ainvoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    logger.info("Retrieved %d chunks", len(docs))
    #logger.info("Context:\n%s", context)

    prompt_value = _PROMPT.invoke({"context": context, "question": question})
    logger.info("Prompt sent to LLM:\n%s", prompt_value.to_string())

    reply = await (llm | StrOutputParser()).ainvoke(prompt_value)
    return reply

