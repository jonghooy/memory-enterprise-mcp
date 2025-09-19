"""
Google Docs Reader PoC using LlamaIndex.

This PoC demonstrates:
1. Authenticating with Google Docs API
2. Reading documents from Google Docs
3. Converting to LlamaIndex Document format
4. Creating embeddings and storing in vector store
"""

import os
import asyncio
from typing import List, Optional
from pathlib import Path

from llama_index.core import Document, VectorStoreIndex
from llama_index.readers.google import GoogleDocsReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleDocsPoCRunner:
    """Runner for Google Docs integration PoC."""

    SCOPES = [
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        embedding_model: str = "BAAI/bge-m3"
    ):
        """Initialize the PoC runner."""
        self.credentials_file = credentials_file
        self.token_file = token_file

        # Configure LlamaIndex settings
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=embedding_model,
            trust_remote_code=True
        )
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50

        self.creds = None
        self.docs_reader = None

    def authenticate(self) -> Credentials:
        """Authenticate with Google APIs."""
        creds = None

        # Check if token file exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(
                self.token_file, self.SCOPES
            )

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download credentials from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.creds = creds
        return creds

    def list_documents(self, max_results: int = 10) -> List[dict]:
        """List available Google Docs."""
        service = build('drive', 'v3', credentials=self.creds)

        # Query for Google Docs only
        results = service.files().list(
            pageSize=max_results,
            q="mimeType='application/vnd.google-apps.document'",
            fields="nextPageToken, files(id, name, createdTime, modifiedTime)"
        ).execute()

        documents = results.get('files', [])

        if not documents:
            print("No documents found.")
            return []

        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"  - {doc['name']} (ID: {doc['id']})")

        return documents

    async def load_document(self, doc_id: str) -> List[Document]:
        """Load a single Google Doc by ID."""
        if not self.docs_reader:
            self.docs_reader = GoogleDocsReader()

        try:
            # Load document
            documents = self.docs_reader.load_data(document_ids=[doc_id])

            print(f"Loaded document with {len(documents)} pages/sections")

            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source': 'google_docs',
                    'doc_id': doc_id,
                    'loader': 'GoogleDocsReader'
                })

            return documents

        except Exception as e:
            print(f"Error loading document {doc_id}: {e}")
            return []

    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create vector index from documents."""
        # Parse documents into nodes
        parser = SentenceSplitter(
            chunk_size=Settings.chunk_size,
            chunk_overlap=Settings.chunk_overlap
        )

        nodes = parser.get_nodes_from_documents(documents)
        print(f"Created {len(nodes)} nodes from documents")

        # Create index
        index = VectorStoreIndex(nodes)

        return index

    async def run_poc(self):
        """Run the complete PoC."""
        print("=" * 60)
        print("Google Docs Reader PoC")
        print("=" * 60)

        # Step 1: Authenticate
        print("\n1. Authenticating with Google...")
        try:
            self.authenticate()
            print("   ✅ Authentication successful")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return

        # Step 2: List documents
        print("\n2. Listing available documents...")
        documents = self.list_documents(max_results=5)

        if not documents:
            print("   No documents to process")
            return

        # Step 3: Load first document
        first_doc = documents[0]
        print(f"\n3. Loading document: {first_doc['name']}...")

        loaded_docs = await self.load_document(first_doc['id'])

        if not loaded_docs:
            print("   Failed to load document")
            return

        # Show sample content
        sample_text = loaded_docs[0].text[:500] if loaded_docs[0].text else "No content"
        print(f"   Sample content: {sample_text}...")

        # Step 4: Create index
        print("\n4. Creating vector index...")
        index = self.create_index(loaded_docs)
        print("   ✅ Index created successfully")

        # Step 5: Test search
        print("\n5. Testing search capabilities...")
        query_engine = index.as_query_engine()

        test_query = "What is the main topic of this document?"
        print(f"   Query: {test_query}")

        response = query_engine.query(test_query)
        print(f"   Response: {response}")

        print("\n" + "=" * 60)
        print("PoC Complete!")
        print("=" * 60)

    def test_wiki_links(self, text: str) -> List[str]:
        """Test wiki-link extraction from text."""
        import re

        # Pattern to match [[entity]] links
        pattern = r'\[\[([^\]]+)\]\]'

        entities = re.findall(pattern, text)

        if entities:
            print(f"Found {len(entities)} wiki-links:")
            for entity in entities:
                print(f"  - [[{entity}]]")
        else:
            print("No wiki-links found")

        return entities


async def main():
    """Main entry point for the PoC."""
    runner = GoogleDocsPoCRunner()

    # Run the full PoC
    await runner.run_poc()

    # Test wiki-link extraction
    print("\n" + "=" * 60)
    print("Wiki-Link Extraction Test")
    print("=" * 60)

    sample_text = """
    This document discusses the [[Project Alpha]] initiative.
    The team, led by [[John Smith]], is working on integrating
    [[Machine Learning]] capabilities into our [[Customer Portal]].
    """

    runner.test_wiki_links(sample_text)


if __name__ == "__main__":
    # Note: To run this PoC, you need:
    # 1. Google Cloud project with Docs API enabled
    # 2. OAuth 2.0 credentials (download as credentials.json)
    # 3. Run the script and complete OAuth flow

    print("""
    Prerequisites:
    1. Enable Google Docs API in Google Cloud Console
    2. Create OAuth 2.0 credentials
    3. Download credentials as 'credentials.json'
    4. Place in the same directory as this script
    """)

    # Check for credentials file
    if not os.path.exists("credentials.json"):
        print("ERROR: credentials.json not found!")
        print("Please follow the prerequisites above.")
    else:
        # Run the PoC
        asyncio.run(main())