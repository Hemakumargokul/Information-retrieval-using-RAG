from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models import BaseChatModel
from services.vector_store.base import BaseVectorStore

_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the question based only on the following context:

{context}

Question: {question}

Answer:""")

def build_rag_chain(llm: BaseChatModel, vector_store: BaseVectorStore):
    retriever = vector_store.get_retriever()
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | _PROMPT
        | llm
        | StrOutputParser()
    )

async def ask(question: str, llm: BaseChatModel, vector_store: BaseVectorStore) -> str:
    chain = build_rag_chain(llm, vector_store)
    return await chain.ainvoke(question)

