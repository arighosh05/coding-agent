import pickle
import numpy as np
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import AsyncOpenAI
from openai import OpenAI
import faiss
import os
from typing import List, Dict, Any
from tqdm import tqdm

OPENAI_API_KEY = "api-key"


class KnowledgeStore:

    def __init__(self, name: str):
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        self.db_path = f"./data/{name}/contextual_vector_db.pkl"
        self.openai_client_synthesizer = OpenAI(api_key=OPENAI_API_KEY)
        self.openai_client_embeddings = AsyncOpenAI(api_key=OPENAI_API_KEY)

        self.token_counts = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_creation': 0
        }
        self.token_lock = threading.Lock()
        self.index = None  # FAISS index

    def situate_context(self, doc: str, chunk: str) -> tuple[str, Any]:
        """generate contextual summaries of chunks for search optimization."""

        DOCUMENT_CONTEXT_PROMPT = f"""
        <document>
        {doc}
        </document>
        """

        CHUNK_CONTEXT_PROMPT = f"""
        Here is the chunk we want to situate within the whole document
        <chunk>
        {chunk}
        </chunk>

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        Answer only with the succinct context and nothing else.
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant that helps with contextual search retrieval."},
            {"role": "user", "content": DOCUMENT_CONTEXT_PROMPT},
            {"role": "user", "content": CHUNK_CONTEXT_PROMPT}
        ]

        response = self.openai_client_synthesizer.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.0  # keeping it deterministic for consistency
        )

        output_text = response.choices[0].message.content
        token_usage = response.usage

        return output_text, token_usage

    async def load_data(self, dataset: List[Dict[str, Any]], parallel_threads: int = 1):
        if self.embeddings and self.metadata:
            print("Vector database is already loaded. Skipping data loading.")
            return
        if os.path.exists(self.db_path):
            print("Loading vector database from disk.")
            await self.load_db()
            return

        texts_to_embed = []
        metadata = []
        total_chunks = sum(len(doc['chunks']) for doc in dataset)

        def process_chunk(doc, chunk):
            # generate contextualized text for each chunk
            contextualized_text, usage = self.situate_context(doc['content'], chunk['content'])

            with self.token_lock:
                self.token_counts['input'] += usage.total_tokens
                self.token_counts['output'] += usage.completion_tokens

            return {
                # append context to the original text chunk
                'text_to_embed': f"{chunk['content']}\n\n{contextualized_text}",
                'metadata': {
                    'doc_id': doc['doc_id'],
                    'original_uuid': doc['original_uuid'],
                    'chunk_id': chunk['chunk_id'],
                    'original_index': chunk['original_index'],
                    'original_content': chunk['content'],
                    'contextualized_content': contextualized_text
                }
            }

        print(f"processing {total_chunks} chunks with {parallel_threads} threads")
        with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
            futures = []
            for doc in dataset:
                for chunk in doc['chunks']:
                    futures.append(executor.submit(process_chunk, doc, chunk))

            for future in tqdm(as_completed(futures), total=total_chunks, desc="processing chunks"):
                result = future.result()
                texts_to_embed.append(result['text_to_embed'])
                metadata.append(result['metadata'])

        await self._embed_and_store(texts_to_embed, metadata)
        self.save_db()

        # Logging token usage
        print(f"contextual vector database loaded and saved. total chunks processed: {len(texts_to_embed)}")
        print(f"total input tokens: {self.token_counts['input']}")
        print(f"total output tokens: {self.token_counts['output']}")

    async def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        batch_size = 128
        tasks = []

        async def fetch_embeddings(batch):
            response = await self.openai_client_embeddings.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            return [item.embedding for item in response.data]

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            tasks.append(fetch_embeddings(batch))

        results = await asyncio.gather(*tasks)  # Run embedding requests in parallel
        self.embeddings = [embedding for batch in results for embedding in batch]
        self.metadata = data

    async def build_index(self):
        """builds a FAISS index for fast similarity search."""

        if self.embeddings:
            d = len(self.embeddings[0])  # dimension of vectors
            self.index = faiss.IndexFlatL2(d)
            self.index.add(np.array(self.embeddings, dtype=np.float32))

    async def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """performs fast nearest-neighbor search using FAISS."""

        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            response = await self.openai_client_embeddings.embeddings.create(
                model="text-embedding-3-small",
                input=[query]
            )
            query_embedding = np.array(response.data[0].embedding, dtype=np.float32)
            self.query_cache[query] = query_embedding

        if self.index is None:
            await self.build_index()

        _, top_indices = self.index.search(query_embedding.reshape(1, -1), k)
        top_indices = top_indices[0]  # extract top-k indices

        top_results = [
            {"metadata": self.metadata[idx], "similarity": None}
            for idx in top_indices
        ]
        return top_results

    def save_db(self):
        # Convert query_cache numpy arrays to lists for serialization
        serializable_cache = {}
        for query, embedding in self.query_cache.items():
            serializable_cache[query] = embedding.tolist()

        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "query_cache": serializable_cache,
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)

    async def load_db(self):
        if not os.path.exists(self.db_path):
            raise ValueError("vector database file not found. use load_data to create a new database.")
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]

        # Convert query_cache lists back to numpy arrays
        self.query_cache = {}
        for query, embedding_list in data["query_cache"].items():
            self.query_cache[query] = np.array(embedding_list, dtype=np.float32)
