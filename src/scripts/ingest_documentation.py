#!/usr/bin/env python3
# scripts/ingest_documentation.py

import os
import sys
import argparse
from pathlib import Path
import time

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ..modules.knowledge_store import KnowledgeStore

def main():
    parser = argparse.ArgumentParser(description="Ingest documentation into the knowledge store")
    parser.add_argument("--path", required=True, help="Path to file or directory to ingest")
    parser.add_argument("--extensions", nargs="+", default=['.py', '.md', '.txt', '.js', '.html', '.css'],
                        help="File extensions to ingest (for directories)")
    parser.add_argument("--output", default="knowledge_store.json", help="Output path for document store")

    args = parser.parse_args()

    # Initialize knowledge store
    store = KnowledgeStore()

    path = Path(args.path)
    start_time = time.time()

    if path.is_file():
        print(f"Ingesting file: {path}")
        store.ingest_documentation(str(path))
        print(f"Successfully ingested {path}")
    elif path.is_dir():
        print(f"Ingesting directory: {path}")
        print("This may take a while for large directories...")
        store.ingest_directory(str(path), args.extensions)
        print(f"Successfully ingested directory: {path}")
    else:
        print(f"Error: {path} is not a valid file or directory")
        return 1

    # Save the documents
    store.save_documents(args.output)

    elapsed_time = time.time() - start_time
    print(f"Ingested {len(store.documents)} document chunks in {elapsed_time:.2f} seconds")
    print(f"Document information saved to {args.output}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
