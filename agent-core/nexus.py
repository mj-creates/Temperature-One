"""
Nexus (Agent 01) - Front Desk & Supervisor Agent
The central orchestration hub for the intelligent multi-agent Academic Advising System.
"""

import sys
from pathlib import Path
from typing import Optional, Any

# Add current directory to path if needed
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .agent_4_background_check import Agent4BackgroundCheck
except ImportError:
    from agent_4_background_check import Agent4BackgroundCheck


class NexusAgent:
    """
    Agent 1 (The Front Desk): Nexus
    Sole Responsibility: Take the input from the user, orchestrate pipeline, and hand off to the next agent.
    """
    
    def __init__(self, next_agent: Optional[Any] = None):
        # Default next agent in the pipeline is Agent 4 (State Synthesizer / Background Check)
        self.next_agent = next_agent if next_agent is not None else Agent4BackgroundCheck()

    def receive_student(self, reg_number: str, name: str, goal: Optional[str] = None) -> Any:
        """
        Phase 1: Greet, Ask Goal (or accept passed goal), and Hand Off to downstream agent.
        """
        # 1. Greet the user warmly
        print(f"Hello {name}! Welcome to your Academic Advising session. I'm Nexus, your front desk advisor.")
        
        # 2. Take the user's goal if not already provided
        if not goal:
            try:
                goal = input("\nWhat is your primary academic or career goal right now? (e.g., Graduate early, specialize in AI, clear backlogs, etc.)\n> ")
            except (EOFError, KeyboardInterrupt):
                goal = "General Academic Degree Progression"
        
        # 3. Hand off to the next agent (Agent 4: State / Background Check)
        print("\n[Nexus] Got it! Handing your details over to our background check system...")
        
        if self.next_agent:
            # Pass all the collected input to the next agent
            if hasattr(self.next_agent, "process_student"):
                return self.next_agent.process_student(reg_number, name, goal)
            elif hasattr(self.next_agent, "inspect_student_id"):
                return self.next_agent.inspect_student_id(reg_number)
            elif hasattr(self.next_agent, "run"):
                return self.next_agent.run(reg_number)
        
        print("\n[SYSTEM HALT] There is no next agent connected to receive this input.")
        return None


if __name__ == '__main__':
    # Simulating a student walking up to the front desk with default Agent 4 connected
    nexus = NexusAgent()
    response = nexus.receive_student("REG1001", "Student", goal="AI Researcher")
    print("\n[Nexus Received Response from Agent 4]:")
    print(response)
