"""
Codex (Agent 05) - Graph-RAG Policy Engine
"""
import re

class Agent5Codex:
    """
    Agent 5: Codex
    Isolated knowledge-retrieval microservice. Queries the university rulebook and course graph.
    Returns absolute, verified facts with citations to Nexus or Matrix.
    """
    
    def __init__(self):
        # Mock Graph-RAG Knowledge Base (Vector/Graph Context Window)
        self.knowledge_base = {
            "operating systems": {
                "Target Subject": "Operating Systems Architecture",
                "Required Prerequisites": ["Computer Architecture & Microprocessors", "Data Structures and Algorithms"],
                "Credit Value": 4,
                "Special Rules": "NONE",
                "Graph Citation": "[Source: CS_Curriculum_Section_3.2_Node_OS]"
            },
            "database management systems": {
                "Target Subject": "Database Management Systems & SQL",
                "Required Prerequisites": ["Object-Oriented Programming with Java"],
                "Credit Value": 4,
                "Special Rules": "NONE",
                "Graph Citation": "[Source: CS_Curriculum_Section_3.1_Node_DBMS]"
            },
            "maximum credit limit": {
                "Target Subject": "Semester Credit Limit",
                "Required Prerequisites": "NONE",
                "Credit Value": 22,
                "Special Rules": "Students on academic probation are strictly limited to 15 credits. Override requires Dean approval.",
                "Graph Citation": "[Source: Univ_Policy_Handbook_Page_14_Credit_Limits]"
            }
        }

    def query_policy(self, query_string: str) -> str:
        """
        Ingests a targeted query string.
        Retrieves matching rules from the Graph-RAG context.
        Outputs strictly the required schema or NO_DATA_FOUND.
        """
        query_lower = query_string.lower()
        
        # 1 & 2. INGEST & RETRIEVE
        matched_context = None
        for key in self.knowledge_base:
            if key in query_lower:
                matched_context = self.knowledge_base[key]
                break
                
        # Zero Hallucination Constraint: If not found, return strictly "NO_DATA_FOUND"
        if not matched_context:
            return "NO_DATA_FOUND"
            
        # 3 & 4. EXTRACT & FORMAT
        prereqs = matched_context["Required Prerequisites"]
        if isinstance(prereqs, list):
            prereqs_str = ", ".join(prereqs)
        else:
            prereqs_str = str(prereqs)
            
        output = (
            "**Policy Constraints:**\n"
            f"- **Target Subject:** {matched_context['Target Subject']}\n"
            f"- **Required Prerequisites:** {prereqs_str}\n"
            f"- **Credit Value:** {matched_context['Credit Value']}\n"
            f"- **Special Rules:** {matched_context['Special Rules']}\n"
            f"- **Graph Citation:** {matched_context['Graph Citation']}"
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
