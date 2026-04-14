

# ===========================================
# rag_tool.py
# ===========================================
# RAG as Tool - now using FAISS!
# Replaced ChromaDB which breaks on
# Python 3.14 due to opentelemetry.
# FAISS is simpler and works everywhere!
# ===========================================

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)
from langchain_community.vectorstores import (
    FAISS)
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader)
import tempfile
import os


class RAGTool:
    """
    RAG as a tool for MCP.
    Uses FAISS - works on Python 3.14!
    Works on Streamlit Cloud! ✅
    MCP treats this like any other tool!
    """

    def __init__(self, openai_key: str):
        """Initialize RAG Tool."""
        self.openai_key = openai_key
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)
        self.doc_count = 0
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """Load and index a PDF."""
        tmp_path = None

        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Read with pypdf
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            if not documents:
                return False, (
                    "PDF appears empty!")

            documents = [
                d for d in documents
                if len(
                    d.page_content.strip()) > 50
            ]

            if not documents:
                return False, (
                    "No readable text found!")

            # Split into chunks
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # Store in FAISS
            if self.vectorstore is None:
                self.vectorstore = (
                    FAISS.from_documents(
                        chunks,
                        self.embeddings))
            else:
                new_store = (
                    FAISS.from_documents(
                        chunks,
                        self.embeddings))
                self.vectorstore.merge_from(
                    new_store)

            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            return True, len(chunks)

        except Exception as e:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            return False, str(e)

    def search(self,
               query: str,
               k: int = 4) -> str:
        """Search documents as MCP tool."""
        if self.vectorstore is None:
            return None

        try:
            docs = self.vectorstore\
                .similarity_search(query, k=k)

            if not docs:
                return None

            context = ""
            for i, doc in enumerate(docs):
                page = doc.metadata.get(
                    'page', '?')
                source = doc.metadata.get(
                    'source', 'Document')
                context += (
                    f"[Section {i+1} - "
                    f"Page {page} - "
                    f"From: {source}]\n"
                    f"{doc.page_content}\n\n"
                    f"{'─' * 30}\n\n")
            return context

        except Exception:
            return None

    def has_documents(self) -> bool:
        """Check if documents loaded."""
        return self.vectorstore is not None

    def get_loaded_files(self) -> list:
        """Return loaded filenames."""
        return self.loaded_files

    def clear_documents(self):
        """Clear all documents."""
        self.vectorstore = None
        self.doc_count = 0
        self.loaded_files = []