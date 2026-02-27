from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from services.vector_store.base import BaseVectorStore

def load_documents(directory: str) -> list[Document]:
    pdf_loader = DirectoryLoader(directory, glob="**/*.pdf", loader_cls = PyPDFLoader)
    return pdf_loader.load()

def chunk_documents(documents: list[Document], chunk_size:int = 1000, chunk_overlap:int = 200) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

def ingest(directory:str, vector_store: BaseVectorStore) -> int:
    docs = load_documents(directory)
    chunks = chunk_documents(docs)
    vector_store.add_documents(chunks)
    return len(chunks)

