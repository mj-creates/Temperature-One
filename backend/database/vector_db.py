import uuid
from typing import List, Dict, Any

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class PolicyVectorDB:
    """
    Graph-RAG Vector Database for Academic Policies.
    Stores and retrieves university rules using semantic search.
    """
    def __init__(self):
        self.is_mock = not CHROMA_AVAILABLE
        if not self.is_mock:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(name="academic_policies")
            self._seed_policies()
        else:
            # Fallback mock for environments without chromadb installed
            self._mock_data = self._get_seed_data()

    def _get_seed_data(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "policy_001",
                "text": "The maximum credit limit per semester is 22 credits. Students on academic probation are strictly limited to 15 credits.",
                "metadata": {"source": "Univ_Policy_Handbook_Page_14", "type": "credit_limit"}
            },
            {
                "id": "policy_002",
                "text": "Operating Systems Architecture requires Computer Architecture & Microprocessors and Data Structures and Algorithms as prerequisites.",
                "metadata": {"source": "CS_Curriculum_Section_3.2", "type": "prerequisite", "subject": "Operating Systems Architecture"}
            },
            {
                "id": "policy_003",
                "text": "Database Management Systems & SQL requires Object-Oriented Programming with Java as a prerequisite.",
                "metadata": {"source": "CS_Curriculum_Section_3.1", "type": "prerequisite", "subject": "Database Management Systems & SQL"}
            },
            {
                "id": "policy_004",
                "text": "Machine Learning Systems & Algorithms requires Probability and Applied Statistics and Linear Algebra & Vector Spaces as prerequisites.",
                "metadata": {"source": "CS_Curriculum_Section_4.1", "type": "prerequisite", "subject": "Machine Learning Systems & Algorithms"}
            }
        ]

    def _seed_policies(self):
        # Only seed if empty
        if self.collection.count() == 0:
            seed_data = self._get_seed_data()
            self.collection.add(
                documents=[item["text"] for item in seed_data],
                metadatas=[item["metadata"] for item in seed_data],
                ids=[item["id"] for item in seed_data]
            )

    def query_policy(self, query: str, n_results: int = 1) -> Dict[str, Any]:
        """
        Retrieves the most semantically relevant policy for the given query.
        """
        if self.is_mock:
            # Simple keyword matching fallback
            query_lower = query.lower()
            for item in self._mock_data:
                # Basic heuristic check
                if "operating system" in query_lower and "operating system" in item["text"].lower():
                    return {"text": item["text"], "metadata": item["metadata"]}
                if "credit limit" in query_lower and "credit limit" in item["text"].lower():
                    return {"text": item["text"], "metadata": item["metadata"]}
                if "database" in query_lower and "database" in item["text"].lower():
                    return {"text": item["text"], "metadata": item["metadata"]}
                if "machine learning" in query_lower and "machine learning" in item["text"].lower():
                    return {"text": item["text"], "metadata": item["metadata"]}
            return None

        # Actual ChromaDB Semantic Search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results and results['documents'] and len(results['documents'][0]) > 0:
            return {
                "text": results['documents'][0][0],
                "metadata": results['metadatas'][0][0]
            }
        return None

# Singleton instance
vector_db = PolicyVectorDB()
