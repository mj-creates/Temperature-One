import json
import sys
from pathlib import Path

# Ensure directory is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from nexus import NexusAgent
from agent_4_background_check import Agent4BackgroundCheck
from agent_3_vector import Agent3Vector

def test_full_pipeline():
    print("--- STARTING 3-AGENT PIPELINE TEST ---")
    
    # 1. Initialize Agents
    agent_3 = Agent3Vector()
    agent_4 = Agent4BackgroundCheck()
    
    # Wire Agent 4 into Agent 1 (Nexus)
    agent_1 = NexusAgent(next_agent=agent_4)
    
    # 2. Nexus takes input and passes to Agent 4
    student_id = "REG1001"
    name = "Student Test"
    goal = "Software Engineer"
    
    print(f"\n[STEP 1] Agent 1 (Nexus) takes input for {student_id} and passes to Agent 4 (State)...")
    # We pass the goal directly for automated testing instead of waiting for `input()`
    state_json = agent_1.receive_student(student_id, name, goal=goal)
    
    print("\n[STEP 2] Agent 4 (State) Database Check Complete. JSON Output Received:")
    print(state_json)
    
    # 3. Pass to Vector (Agent 3) 
    # Since Matrix (Agent 2) doesn't exist, we mock the schedule
    print("\n[STEP 3] Passing goal and (mock) Matrix schedule to Agent 3 (Vector)...")
    
    mock_matrix_schedule = {
        "Semester 3": ["Database Management Systems & SQL", "Operating Systems Architecture"]
    }
    
    vector_output = agent_3.generate_momentum_plan(student_goal=goal, matrix_schedule=mock_matrix_schedule)
    print("\n[Agent 3 Vector Output]:")
    print(vector_output)
    
    print("\n--- PIPELINE TEST COMPLETE ---")

if __name__ == "__main__":
    test_full_pipeline()
