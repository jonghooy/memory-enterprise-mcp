"""
Pinecone Namespace Isolation PoC.

This PoC demonstrates:
1. Creating isolated namespaces for multi-tenant data
2. Inserting vectors into tenant-specific namespaces
3. Querying within namespace boundaries
4. Verifying complete data isolation between tenants
"""

import os
import time
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import pinecone
from pinecone import Pinecone, ServerlessSpec


@dataclass
class TenantData:
    """Sample tenant data for testing."""

    tenant_id: str
    namespace: str
    documents: List[str]
    vectors: Optional[List[List[float]]] = None


class PineconeIsolationPoC:
    """PoC for demonstrating Pinecone namespace isolation."""

    def __init__(
        self,
        api_key: str,
        environment: str = "us-east-1",
        index_name: str = "memory-agent-poc",
        dimension: int = 1024
    ):
        """Initialize the PoC runner."""
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension

        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        self.index = None

    def setup_index(self):
        """Create or connect to Pinecone index."""
        print(f"Setting up Pinecone index: {self.index_name}")

        # Check if index exists
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"Creating new index...")

            # Create serverless index
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=self.environment
                )
            )

            # Wait for index to be ready
            time.sleep(5)
            print(f"  ✅ Index created")
        else:
            print(f"  ℹ️ Index already exists")

        # Connect to index
        self.index = self.pc.Index(self.index_name)

        # Get index stats
        stats = self.index.describe_index_stats()
        print(f"  Index stats: {stats}")

    def create_sample_tenants(self) -> List[TenantData]:
        """Create sample tenant data for testing."""
        tenants = []

        # Tenant 1: Tech Company
        tenant1 = TenantData(
            tenant_id="tenant-001",
            namespace="tenant-001-tech-corp",
            documents=[
                "Our Q4 product roadmap includes AI features and cloud migration.",
                "The engineering team is implementing microservices architecture.",
                "Customer feedback shows high satisfaction with our API performance.",
                "Security audit completed successfully with zero critical issues.",
                "New machine learning pipeline reduced processing time by 60%."
            ]
        )

        # Tenant 2: Healthcare Provider
        tenant2 = TenantData(
            tenant_id="tenant-002",
            namespace="tenant-002-health-org",
            documents=[
                "Patient care protocols updated for improved emergency response.",
                "Medical staff training on new diagnostic equipment completed.",
                "HIPAA compliance review passed with no violations found.",
                "Telemedicine platform usage increased by 200% this quarter.",
                "Clinical trial data shows promising results for new treatment."
            ]
        )

        # Tenant 3: Education Institution
        tenant3 = TenantData(
            tenant_id="tenant-003",
            namespace="tenant-003-edu-inst",
            documents=[
                "Student enrollment for spring semester exceeds projections.",
                "New online learning platform launched successfully.",
                "Research grant awarded for quantum computing studies.",
                "Faculty development workshop on innovative teaching methods.",
                "Campus sustainability initiative reduced energy consumption by 30%."
            ]
        )

        tenants = [tenant1, tenant2, tenant3]

        # Generate random vectors for each document
        for tenant in tenants:
            tenant.vectors = [
                np.random.rand(self.dimension).tolist()
                for _ in tenant.documents
            ]

        return tenants

    def insert_tenant_data(self, tenant: TenantData):
        """Insert data for a specific tenant into their namespace."""
        print(f"\nInserting data for {tenant.tenant_id} into namespace: {tenant.namespace}")

        # Prepare vectors with metadata
        vectors = []
        for i, (doc, vec) in enumerate(zip(tenant.documents, tenant.vectors)):
            vectors.append({
                'id': f"{tenant.tenant_id}-doc-{i}",
                'values': vec,
                'metadata': {
                    'tenant_id': tenant.tenant_id,
                    'document': doc,
                    'doc_index': i,
                    'timestamp': time.time()
                }
            })

        # Upsert to tenant-specific namespace
        self.index.upsert(
            vectors=vectors,
            namespace=tenant.namespace
        )

        print(f"  ✅ Inserted {len(vectors)} vectors")

    def query_namespace(
        self,
        namespace: str,
        query_vector: List[float],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Query within a specific namespace."""
        print(f"\nQuerying namespace: {namespace}")

        results = self.index.query(
            namespace=namespace,
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        print(f"  Found {len(results['matches'])} matches:")
        for match in results['matches']:
            print(f"    - Score: {match['score']:.3f}")
            print(f"      Document: {match['metadata']['document'][:60]}...")

        return results

    def verify_isolation(self, tenants: List[TenantData]):
        """Verify that namespaces are completely isolated."""
        print("\n" + "=" * 60)
        print("VERIFYING NAMESPACE ISOLATION")
        print("=" * 60)

        # Use first document vector from tenant 1 as query
        query_vector = tenants[0].vectors[0]

        print("\n1. Querying Tenant 1's namespace with Tenant 1's data:")
        results_1 = self.query_namespace(
            namespace=tenants[0].namespace,
            query_vector=query_vector,
            top_k=5
        )

        print("\n2. Querying Tenant 2's namespace with Tenant 1's data:")
        results_2 = self.query_namespace(
            namespace=tenants[1].namespace,
            query_vector=query_vector,
            top_k=5
        )

        print("\n3. Querying Tenant 3's namespace with Tenant 1's data:")
        results_3 = self.query_namespace(
            namespace=tenants[2].namespace,
            query_vector=query_vector,
            top_k=5
        )

        # Verify isolation
        print("\n" + "=" * 60)
        print("ISOLATION VERIFICATION RESULTS:")
        print("=" * 60)

        # Check that only tenant 1's namespace has tenant 1's data
        tenant1_ids = {f"tenant-001-doc-{i}" for i in range(len(tenants[0].documents))}

        found_in_1 = {m['id'] for m in results_1['matches']}
        found_in_2 = {m['id'] for m in results_2['matches']}
        found_in_3 = {m['id'] for m in results_3['matches']}

        print(f"\nTenant 1 IDs found in:")
        print(f"  - Tenant 1 namespace: {len(found_in_1 & tenant1_ids)}/{len(tenant1_ids)}")
        print(f"  - Tenant 2 namespace: {len(found_in_2 & tenant1_ids)}/{len(tenant1_ids)}")
        print(f"  - Tenant 3 namespace: {len(found_in_3 & tenant1_ids)}/{len(tenant1_ids)}")

        # Verify metadata isolation
        print(f"\nMetadata check:")
        for result, tenant_id in [
            (results_1, "tenant-001"),
            (results_2, "tenant-002"),
            (results_3, "tenant-003")
        ]:
            if result['matches']:
                found_tenant_ids = {
                    m['metadata'].get('tenant_id')
                    for m in result['matches']
                    if 'metadata' in m
                }
                print(f"  - Namespace for {tenant_id}: {found_tenant_ids}")

        # Final verdict
        isolation_verified = (
            len(found_in_2 & tenant1_ids) == 0 and
            len(found_in_3 & tenant1_ids) == 0
        )

        print("\n" + "=" * 60)
        if isolation_verified:
            print("✅ ISOLATION VERIFIED: Data is completely isolated between tenants")
        else:
            print("❌ ISOLATION FAILED: Data leakage detected between tenants!")
        print("=" * 60)

        return isolation_verified

    def cleanup_namespaces(self, tenants: List[TenantData]):
        """Clean up test data from namespaces."""
        print("\nCleaning up test data...")

        for tenant in tenants:
            # Delete all vectors in namespace
            ids_to_delete = [
                f"{tenant.tenant_id}-doc-{i}"
                for i in range(len(tenant.documents))
            ]

            self.index.delete(
                ids=ids_to_delete,
                namespace=tenant.namespace
            )

            print(f"  ✅ Cleaned namespace: {tenant.namespace}")

    def run_poc(self):
        """Run the complete PoC."""
        print("=" * 60)
        print("PINECONE NAMESPACE ISOLATION POC")
        print("=" * 60)

        # Step 1: Setup index
        self.setup_index()

        # Step 2: Create sample tenants
        print("\nCreating sample tenant data...")
        tenants = self.create_sample_tenants()
        print(f"  ✅ Created {len(tenants)} tenants")

        # Step 3: Insert data for each tenant
        for tenant in tenants:
            self.insert_tenant_data(tenant)

        # Wait for indexing
        print("\nWaiting for indexing to complete...")
        time.sleep(2)

        # Step 4: Verify isolation
        isolation_success = self.verify_isolation(tenants)

        # Step 5: Test statistics per namespace
        print("\n" + "=" * 60)
        print("NAMESPACE STATISTICS")
        print("=" * 60)

        stats = self.index.describe_index_stats()
        print(f"\nOverall index stats:")
        print(f"  - Total vectors: {stats['total_vector_count']}")
        print(f"  - Dimension: {stats['dimension']}")

        if 'namespaces' in stats:
            print(f"\nPer-namespace stats:")
            for ns_name, ns_stats in stats['namespaces'].items():
                print(f"  - {ns_name}: {ns_stats['vector_count']} vectors")

        # Step 6: Cleanup
        cleanup = input("\nCleanup test data? (y/n): ")
        if cleanup.lower() == 'y':
            self.cleanup_namespaces(tenants)

        print("\n" + "=" * 60)
        print("POC COMPLETE!")
        print("=" * 60)

        return isolation_success


def main():
    """Main entry point for the PoC."""
    # Get API key from environment
    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        print("ERROR: PINECONE_API_KEY environment variable not set!")
        print("Please set it with your Pinecone API key.")
        return

    # Run the PoC
    poc = PineconeIsolationPoC(api_key=api_key)
    success = poc.run_poc()

    if success:
        print("\n✅ Pinecone namespace isolation is working correctly!")
        print("This confirms we can safely use Pinecone for multi-tenant data.")
    else:
        print("\n❌ Namespace isolation test failed!")
        print("Further investigation needed before using in production.")


if __name__ == "__main__":
    print("""
    Prerequisites:
    1. Sign up for Pinecone account (free tier is sufficient)
    2. Get your API key from Pinecone console
    3. Set PINECONE_API_KEY environment variable

    Example:
    export PINECONE_API_KEY="your-api-key-here"
    """)

    main()