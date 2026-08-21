"""
Matrix Agent Module (Agent 2 - The Matrix)
"""

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .agent_matrix import MatrixAgent, run_matrix
except ImportError:
    from agent_matrix import MatrixAgent, run_matrix

__all__ = ["MatrixAgent", "run_matrix"]

if __name__ == "__main__":
    agent = MatrixAgent()
    target = sys.argv[1] if len(sys.argv) > 1 else "Sub_4_2"
    student = sys.argv[2] if len(sys.argv) > 2 else "REG1001"
    print(agent.compute_path_from_db(student, target))
