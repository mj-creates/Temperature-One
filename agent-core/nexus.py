class NexusAgent:
    """
    Agent 1 (The Front Desk): Nexus
    Sole Responsibility: Take the input from the user and hand it to the next agent.
    """
    
    def __init__(self, next_agent=None):
        # Nexus only knows about the next agent in line (Agent 4: State)
        self.next_agent = next_agent

    def receive_student(self, reg_number: str, name: str):
        """
        Phase 1: Greet, Ask Goal, and Hand Off.
        """
        # 1. Greet the user warmly
        print(f"Hello {name}! Welcome to your Academic Advising session. I'm Nexus, your front desk advisor.")
        
        # 2. Take the user's goal
        goal = input("\nWhat is your primary academic or career goal right now? (e.g., Graduate early, specialize in AI, clear backlogs, etc.)\n> ")
        
        # 3. Give it to the next agent (Agent 4: State) and that's it!
        print("\n[Nexus] Got it! Handing your details over to our background check system...")
        
        if self.next_agent:
            # Pass all the collected input to the next agent
            return self.next_agent.process_student(reg_number, name, goal)
        else:
            print("\n[SYSTEM HALT] There is no next agent connected to receive this input.")

if __name__ == '__main__':
    # Nexus is created purely as the front desk.
    nexus = NexusAgent()
    # Simulating a student walking up to the front desk
    nexus.receive_student("REG1001", "Student")
