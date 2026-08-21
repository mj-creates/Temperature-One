import json

class NexusAgent:
    """
    ROLE AND IDENTITY:
    Nexus (Agent 01), the Supervisor Agent and central orchestration hub for an 
    intelligent multi-agent Academic Advising System.
    """
    
    def __init__(self):
        self.persona = "Professional, highly organized, and empathetic to student stress."
        self.constraints = [
            "DO NOT hallucinate or invent university rules, courses, or credits.",
            "DO NOT give schedule advice based on your own training data. You must ONLY use the outputs provided by your sub-agents.",
            "ALWAYS execute the multi-agent pipeline in the exact sequence outlined below. Do not skip steps or make assumptions."
        ]

    def phase_1_initiation(self, reg_number: str, name: str) -> str:
        """
        PHASE 1: Initiation & Elicitation
        """
        print(f"Hello {name}! Welcome to your Academic Advising session. I'm Nexus, your advisor.")
        goal = input("What is your primary academic or career goal right now? (e.g., Graduate early, specialize in AI, clear backlogs, etc.)\n")
        return goal

    def phase_2_orchestration(self, reg_number: str, goal: str):
        """
        PHASE 2: Orchestration (Invisible to User)
        """
        # 1. CALL State / Agent 04
        state_output = self._call_state_agent(reg_number)
        
        # 2. CALL Matrix / Agent 02
        matrix_output = self._call_matrix_agent(goal, state_output)
        
        # 3. CALL Vector / Agent 03
        vector_output = self._call_vector_agent(matrix_output)
        
        return state_output, matrix_output, vector_output

    def phase_3_synthesis(self, state_output: dict, matrix_output: list, vector_output: list) -> str:
        """
        PHASE 3: Synthesis & Final Output
        """
        summary_section = f"### Section 1: Current Status\n- Credits Earned: {state_output.get('credits_earned', 0)}\n- Credits Required: {state_output.get('credits_required', 0)}\n- Active Backlogs: {', '.join(state_output.get('active_backlogs', ['None']))}\n"
        
        plan_section = "### Section 2: Semester-by-Semester Plan\n"
        for sem in matrix_output:
            plan_section += f"- {sem}\n"
            
        future_section = "### Section 3: Future Scope & Extracurricular Advice\n"
        for step in vector_output:
            future_section += f"- {step}\n"
            
        closing = "\nI'm confident this path will lead you to your goal. Remember, you have our full support every step of the way!"
        
        final_output = f"{summary_section}\n{plan_section}\n{future_section}\n{closing}"
        return final_output

    def run_pipeline(self, reg_number: str, name: str):
        # Phase 1
        goal = self.phase_1_initiation(reg_number, name)
        
        # Phase 2
        state, matrix, vector = self.phase_2_orchestration(reg_number, goal)
        
        # Phase 3
        final_response = self.phase_3_synthesis(state, matrix, vector)
        print(final_response)
        return final_response

    # --- Dummy sub-agent calls for structure ---
    
    def _call_state_agent(self, reg_number: str) -> dict:
        """Agent 04: Query database for total credits, required, and backlogs."""
        # TODO: Implement real database query
        return {
            "credits_earned": 90,
            "credits_required": 120,
            "active_backlogs": []
        }

    def _call_matrix_agent(self, goal: str, state_output: dict) -> list:
        """Agent 02: Graph traversal to build valid schedule clearing backlogs, obeying prerequisites."""
        # TODO: Implement graph traversal logic
        return [
            "Semester 7: Course A, Course B",
            "Semester 8: Course C, Course D"
        ]

    def _call_vector_agent(self, matrix_output: list) -> list:
        """Agent 03: Provide 2-3 specific actionable career/certification/internship steps."""
        # TODO: Implement Vector analysis
        return [
            "Complete AWS Cloud Practitioner Certification.",
            "Apply for Software Engineering Internships focusing on AI tooling."
        ]

if __name__ == '__main__':
    agent = NexusAgent()
    agent.run_pipeline("REG123456", "Student")
