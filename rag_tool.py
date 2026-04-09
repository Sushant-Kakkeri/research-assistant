# ===========================================
# rag_tool.py
# ===========================================
# RAG as a Tool for MCP Research Assistant
#
# FIXES IN THIS VERSION:
# - Removed pymupdf (caused build errors)
# - Using pypdf only (works on cloud!)
# - Uses ChromaDB EphemeralClient
# - Works on Streamlit Cloud!
# ===========================================

# Text splitter
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)

# ChromaDB vector store
from langchain_community.vectorstores import (
    Chroma)

# OpenAI embeddings
from langchain_openai import OpenAIEmbeddings

# PDF loader - pypdf only!
from langchain_community.document_loaders import (
    PyPDFLoader)

# ChromaDB in-memory client
import chromadb
from chromadb.config import Settings

# File handling
import tempfile
import os


class RAGTool:
    """
    RAG packaged as a tool for MCP.
    Uses pypdf (no compilation needed!)
    Uses EphemeralClient (in-memory)
    Works perfectly on Streamlit Cloud!
    """

    def __init__(self, openai_key: str):
        """
        Initialize RAG Tool.

        Args:
            openai_key: OpenAI API key
        """
        self.openai_key = openai_key

        # ChromaDB in-memory client
        # No disk permissions needed!
        # Perfect for Streamlit Cloud!
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False
                )
            ))

        # Vector store - empty until PDF loaded
        self.vectorstore = None

        # Convert text to numbers
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)

        # Track loaded pages
        self.doc_count = 0

        # Track loaded filenames
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """
        Load and index a PDF file.
        Uses pypdf only - no compilation!

        Args:
            uploaded_file: Streamlit file

        Returns:
            (True, chunk_count) or
            (False, error_message)
        """
        tmp_path = None

        try:
            # STEP 1: Save to temp file
            # pypdf needs file on disk
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # STEP 2: Read PDF with pypdf
            # Simple and reliable!
            # Works on all platforms!
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            # STEP 3: Validate content
            if not documents:
                return False, (
                    "PDF appears empty "
                    "or image-based!")

            # Filter empty pages
            # Less than 50 chars = blank
            documents = [
                d for d in documents
                if len(
                    d.page_content.strip()) > 50
            ]

            if not documents:
                return False, (
                    "No readable text found! "
                    "Try a Wikipedia PDF.")

            # STEP 4: Split into chunks
            # chunk_size=1000 = ~150 words
            # chunk_overlap=200 = shared chars
            # Prevents cutting answers in half!
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # STEP 5: Store in ChromaDB
            # EphemeralClient = in memory!
            # No disk issues on cloud!
            if self.vectorstore is None:
                # First PDF - create new store
                self.vectorstore = (
                    Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        client=self.chroma_client
                    ))
            else:
                # More PDFs - add to existing
                self.vectorstore.add_documents(
                    documents=chunks)

            # Track what was loaded
            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            # STEP 6: Clean up temp file
            # Windows sometimes locks files
            # so use try/except!
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            # Return success with chunk count
            return True, len(chunks)

        except Exception as e:
            # Clean up even if error occurs
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            # Return failure with error message
            return False, str(e)

    def search(self,
               query: str,
               k: int = 4) -> str:
        """
        Search documents for relevant content.
        MCP calls this exactly like web_search!

        Args:
            query: What to search for
            k:     Number of results to return

        Returns:
            Relevant document sections
            or None if nothing found
        """
        # Can't search if nothing loaded!
        if self.vectorstore is None:
            return None

        try:
            # Find chunks by MEANING
            # Not just keyword matching!
            docs = self.vectorstore\
                .similarity_search(query, k=k)

            if not docs:
                return None

            # Format results with metadata
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
        """Check if documents are loaded."""
        return self.vectorstore is not None

    def get_loaded_files(self) -> list:
        """Return list of loaded filenames."""
        return self.loaded_files

    def clear_documents(self):
        """
        Clear all documents.
        Creates fresh ChromaDB client.
        """
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False
                )
            ))
        self.vectorstore = None
        self.doc_count = 0
        self.loaded_files = []