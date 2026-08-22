"""
Codex (Agent 05) - Graph-RAG Policy Engine
"""
import re
import sys
from pathlib import Path

# Ensure backend can be imported
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR.parent))

from backend.database.vector_db import vector_db

class Agent5Codex:
    """
    Agent 5: Codex
    Isolated knowledge-retrieval microservice. Queries the university rulebook and course graph.
    Returns absolute, verified facts with citations to Nexus or Matrix.
    """
    
    def __init__(self):
        self.vector_db = vector_db

    def query_policy(self, query_string: str) -> str:
        """
        Ingests a targeted query string.
        Retrieves matching rules from the Graph-RAG context via semantic search.
        Outputs strictly the required schema or NO_DATA_FOUND.
        """
        # 1 & 2. INGEST & RETRIEVE (Live Vector Search)
        matched_context = self.vector_db.query_policy(query_string)
        
        # Zero Hallucination Constraint: If not found, return strictly "NO_DATA_FOUND"
        if not matched_context:
            return "NO_DATA_FOUND"
            
        # 3 & 4. EXTRACT & FORMAT
        metadata = matched_context["metadata"]
        text = matched_context["text"]
        
        # Parse fields based on metadata (Simulated extraction for the strict format)
        target = metadata.get("subject", "University Policy")
        
        # In a real pipeline, we'd use an LLM here to format the `text` strictly, 
        # but here we output it mapped to the required schema.
        output = (
            "**Policy Constraints:**\n"
            f"- **Target Subject:** {target}\n"
            f"- **Required Prerequisites:** See Policy Details\n"
            f"- **Credit Value:** See Policy Details\n"
            f"- **Special Rules:** {text}\n"
            f"- **Graph Citation:** [{metadata.get('source', 'Unknown_Source')}]"
        )
        
        return output

if __name__ == "__main__":
    # Test the microservice boundaries and zero-hallucination constraint
    codex = Agent5Codex()
    
    print("--- Test 1: Known Subject Query ---")
    print(codex.query_policy("What are the prerequisites for Operating Systems?"))
    
    print("\n--- Test 2: Known Policy Query ---")
    print(codex.query_policy("What is the maximum credit limit per semester?"))
    
    print("\n--- Test 3: Unknown Subject Query (Zero Hallucination Check) ---")
    print(codex.query_policy("What are the prerequisites for Quantum Computing?"))
