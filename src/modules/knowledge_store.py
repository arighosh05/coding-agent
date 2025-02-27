import os
import json
import re
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeStore:
    """
    Knowledge store for code review agent that implements RAG capabilities.
    Uses scikit-learn for TF-IDF vectorization and cosine similarity search.
    """

    def __init__(self, index_path: str = None):
        """
        Initialize the knowledge store.

        Args:
            index_path: Optional path to load existing documents
        """
        self.documents = []
        self.vectorizer = None
        self.document_vectors = None

        if index_path and os.path.exists(index_path):
            self.load_documents(index_path)

    def _chunk_document(self, content: str, chunk_size: int = 1500, overlap: int = 300) -> List[str]:
        """
        Split document content into overlapping chunks for better retrieval.

        Args:
            content: The document content to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Overlap between consecutive chunks

        Returns:
            List of document chunks
        """
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))

            # Try to find a good breaking point (newline or period)
            if end < len(content):
                # Look for newline or period within the last 100 chars of the chunk
                break_point = max(
                    content.rfind("\n", start, end),
                    content.rfind(". ", start, end)
                )

                if break_point > start + chunk_size // 2:
                    end = break_point + 1

            chunks.append(content[start:end])
            start = end - overlap

        return chunks

    def _extract_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract code blocks from markdown-formatted content.

        Args:
            content: Content potentially containing markdown code blocks

        Returns:
            List of tuples (language, code)
        """
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        # Also capture plain text as context
        text_chunks = re.split(r"```.*?```", content, flags=re.DOTALL)
        text_chunks = [chunk.strip() for chunk in text_chunks if chunk.strip()]

        # Combine code blocks and text
        results = []

        # Add text chunks as context
        for chunk in text_chunks:
            results.append(("text", chunk))

        # Add code blocks with their language
        for lang, code in matches:
            if not lang:
                lang = "unknown"
            results.append((lang, code.strip()))

        return results

    def _build_vector_index(self):
        """Build or rebuild the vector index for search"""
        if not self.documents:
            return

        # Extract document content for vectorization
        doc_contents = [doc["content"] for doc in self.documents]

        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            max_df=0.95,  # Ignore terms that appear in >95% of documents
            min_df=2,     # Ignore terms that appear in fewer than 2 documents
            ngram_range=(1, 2),  # Use unigrams and bigrams
            stop_words='english'
        )

        # Fit and transform documents to TF-IDF vectors
        self.document_vectors = self.vectorizer.fit_transform(doc_contents)

    def ingest_document(self, content: str, metadata: Dict[str, Any] = None) -> None:
        """
        Ingest a document into the knowledge store.

        Args:
            content: The document content
            metadata: Optional metadata about the document
        """
        if metadata is None:
            metadata = {}

        # Process document in chunks
        chunks = self._chunk_document(content)

        # Extract code blocks if present
        code_blocks = self._extract_code_blocks(content)

        # Store document chunks
        doc_id = len(self.documents)

        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "doc_id": doc_id,
                "chunk_id": i,
                "chunk_type": "text"
            })

            # Store document information
            self.documents.append({
                "content": chunk,
                "metadata": chunk_metadata
            })

        # Store code blocks separately
        for lang, code in code_blocks:
            if lang == "text" or not code.strip():
                continue

            block_metadata = metadata.copy()
            block_metadata.update({
                "doc_id": doc_id,
                "chunk_type": "code",
                "language": lang
            })

            # Store document information
            self.documents.append({
                "content": code,
                "metadata": block_metadata
            })

        # Rebuild the vector index
        self._build_vector_index()

    def ingest_documentation(self, file_path: str, metadata: Dict[str, Any] = None) -> None:
        """
        Ingest documentation from a file.

        Args:
            file_path: Path to the documentation file
            metadata: Optional metadata about the document
        """
        if metadata is None:
            metadata = {}

        # Update metadata with file info
        file_path = Path(file_path)
        metadata.update({
            "source": str(file_path),
            "filename": file_path.name,
            "extension": file_path.suffix
        })

        # Read file content
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Ingest document
        self.ingest_document(content, metadata)

    def ingest_directory(self, dir_path: str, extensions: List[str] = None) -> None:
        """
        Ingest all documentation files in a directory.

        Args:
            dir_path: Path to the directory
            extensions: List of file extensions to include (e.g., ['.py', '.md'])
        """
        if extensions is None:
            extensions = ['.py', '.md', '.txt', '.js', '.java', '.html', '.css']

        dir_path = Path(dir_path)

        # Collect all files first
        all_files = []
        for file_path in dir_path.glob("**/*"):
            if file_path.is_file() and file_path.suffix in extensions:
                all_files.append(file_path)

        # Ingest files one by one
        for file_path in all_files:
            metadata = {
                "directory": str(file_path.parent),
                "relative_path": str(file_path.relative_to(dir_path))
            }
            try:
                self.ingest_documentation(str(file_path), metadata)
                print(f"Ingested: {file_path}")
            except Exception as e:
                print(f"Failed to ingest {file_path}: {str(e)}")

        # Build the vector index only once at the end for efficiency
        self._build_vector_index()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge store for relevant information using TF-IDF and cosine similarity.

        Args:
            query: The search query
            k: Number of results to return

        Returns:
            List of document chunks with content and metadata
        """
        if not self.documents or not self.vectorizer or not self.document_vectors:
            return []

        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])

        # Calculate similarity with all documents
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()

        # Get top k results
        top_indices = similarities.argsort()[-k:][::-1]

        # Collect results
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include if there's some similarity
                result = {
                    "content": self.documents[idx]["content"],
                    "metadata": self.documents[idx]["metadata"],
                    "score": float(similarities[idx])
                }
                results.append(result)

        return results

    def get_context_for_code_review(self, code: str, context: str, k: int = 5) -> str:
        """
        Get relevant context for code review by searching the knowledge store.

        Args:
            code: The code to review
            context: The existing context for the code
            k: Number of results to retrieve

        Returns:
            Augmented context with relevant information
        """
        # Combine code and context for better search relevance
        query = f"{context}\n\n{code}"

        # Search for relevant documents
        results = self.search(query, k=k)

        if not results:
            return context

        # Format results as additional context
        additional_context = "Additional relevant information from documentation:\n\n"

        for i, result in enumerate(results):
            content = result["content"]
            metadata = result["metadata"]
            score = result["score"]

            source = metadata.get("source", "Unknown source")
            chunk_type = metadata.get("chunk_type", "text")
            language = metadata.get("language", "") if chunk_type == "code" else ""

            # Format the source path for better readability
            source_path = Path(source)
            readable_source = f"{source_path.name}"
            if metadata.get("relative_path"):
                readable_source = metadata.get("relative_path")

            additional_context += f"--- Document {i+1} from {readable_source} (relevance: {score:.2f}) ---\n"
            if chunk_type == "code":
                additional_context += f"Code snippet ({language}):\n```{language}\n{content}\n```\n\n"
            else:
                additional_context += f"{content}\n\n"

        return f"{context}\n\n{additional_context}"

    def save_documents(self, documents_path: str) -> None:
        """
        Save documents to disk.

        Args:
            documents_path: Path to save document information
        """
        # We can't directly serialize the vectorizer and document vectors,
        # so we'll just save the documents and rebuild the index on load
        with open(documents_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f)

    def load_documents(self, documents_path: str) -> None:
        """
        Load documents from disk and rebuild the vector index.

        Args:
            documents_path: Path to the document information
        """
        with open(documents_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # Rebuild the vector index
        self._build_vector_index()
