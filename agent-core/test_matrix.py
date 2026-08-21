"""
Unit Tests for Agent 2: "The Matrix" (Graph Navigator & Pathfinder).
Tests prerequisite graphs, temporal scheduling, error protocols, and schema validation.
"""

import sys
import json
import unittest
from pathlib import Path

# Add current directory to path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from schemas import (
    MatrixPathResponse,
    MatrixErrorResponse,
    STATUS_VALID,
    STATUS_PATH_UNREACHABLE,
    STATUS_GRAPH_ERROR,
    STATUS_ALREADY_ACHIEVED,
    ERROR_MISSING_CRITICAL_NODE,
    ERROR_CYCLIC_DEPENDENCY,
)
from matrix_graph import GraphNode, PrerequisiteGraph
from matrix_pathfinder import compute_matrix_path
from agent_matrix import MatrixAgent


class TestMatrixGraphAndPathfinding(unittest.TestCase):
    def setUp(self):
        self.agent = MatrixAgent()

    def test_valid_path_generation(self):
        """Tests end-to-end pathfinding for a target course."""
        target = "Sub_4_2"  # Deep Learning (requires Sub_4_1 -> Sub_3_3/Sub_3_5 -> Sub_2_1/Sub_2_3/Sub_2_5 -> Sub_1_1/Sub_1_2)
        res_json = self.agent.compute_path("REG1001", target, completed_nodes=[])
        data = json.loads(res_json)

        self.assertEqual(data["student_id"], "REG1001")
        self.assertEqual(data["target_node"], target)
        self.assertEqual(data["path_status"], STATUS_VALID)
        self.assertGreaterEqual(data["total_steps_required"], 2)
        self.assertIsInstance(data["path_sequence"], list)
        self.assertIsInstance(data["bottlenecks"], list)
        self.assertTrue(len(data["matrix_analysis"]) > 20)

        # Check temporal order: Prerequisites must appear in earlier steps
        step_of_node = {}
        for step in data["path_sequence"]:
            step_num = step["step_number"]
            for nid in step["nodes_to_complete"]:
                step_of_node[nid] = step_num

        # Sub_1_1 must be before Sub_2_1, Sub_2_1 before Sub_3_3, Sub_3_3 before Sub_4_1, Sub_4_1 before Sub_4_2
        self.assertLess(step_of_node["Sub_1_1"], step_of_node["Sub_2_1"])
        self.assertLess(step_of_node["Sub_2_1"], step_of_node["Sub_3_3"])
        self.assertLess(step_of_node["Sub_3_3"], step_of_node["Sub_4_1"])
        self.assertLess(step_of_node["Sub_4_1"], step_of_node["Sub_4_2"])

    def test_state_awareness_completed_nodes(self):
        """Tests that already completed nodes are omitted from the schedule."""
        target = "Sub_4_2"
        completed = ["Sub_1_1", "Sub_1_2", "Sub_2_1", "Sub_2_3", "Sub_2_5"]
        res_json = self.agent.compute_path("REG1001", target, completed_nodes=completed)
        data = json.loads(res_json)

        self.assertEqual(data["path_status"], STATUS_VALID)
        all_scheduled_nodes = [
            nid for step in data["path_sequence"] for nid in step["nodes_to_complete"]
        ]
        for c in completed:
            self.assertNotIn(c, all_scheduled_nodes)

    def test_already_achieved_protocol(self):
        """Tests that target already in completed state triggers ALREADY_ACHIEVED."""
        target = "Sub_4_2"
        res_json = self.agent.compute_path("REG1001", target, completed_nodes=[target])
        data = json.loads(res_json)

        self.assertEqual(data["status"], STATUS_ALREADY_ACHIEVED)
        self.assertIsNone(data["error"])
        self.assertEqual(data["sequence"], [])

    def test_missing_critical_node_unreachable(self):
        """Tests that an unreachable target with missing prerequisites triggers PATH_UNREACHABLE."""
        custom_nodes = [
            {"node_id": "Target_Course", "prerequisites": ["NON_EXISTENT_PREREQ"]},
        ]
        res_json = self.agent.compute_path(
            "REG1001",
            "Target_Course",
            custom_graph_nodes=custom_nodes
        )
        data = json.loads(res_json)

        self.assertEqual(data["status"], STATUS_PATH_UNREACHABLE)
        self.assertEqual(data["error"], ERROR_MISSING_CRITICAL_NODE)
        self.assertEqual(data["sequence"], [])

    def test_cyclic_dependency_detection(self):
        """Tests that circular prerequisites trigger GRAPH_ERROR CYCLIC_DEPENDENCY."""
        custom_nodes = [
            {"node_id": "Node_A", "prerequisites": ["Node_B"]},
            {"node_id": "Node_B", "prerequisites": ["Node_C"]},
            {"node_id": "Node_C", "prerequisites": ["Node_A"]},
            {"node_id": "Target_Node", "prerequisites": ["Node_C"]},
        ]
        res_json = self.agent.compute_path(
            "REG1001",
            "Target_Node",
            custom_graph_nodes=custom_nodes
        )
        data = json.loads(res_json)

        self.assertEqual(data["status"], STATUS_GRAPH_ERROR)
        self.assertEqual(data["error"], ERROR_CYCLIC_DEPENDENCY)
        self.assertEqual(data["sequence"], [])

    def test_corequisite_scheduling(self):
        """Tests that co-requisite courses are scheduled in the same step."""
        custom_nodes = [
            {"node_id": "Coreq_A", "credits": 3, "prerequisites": [], "corequisites": ["Coreq_B"]},
            {"node_id": "Coreq_B", "credits": 3, "prerequisites": [], "corequisites": ["Coreq_A"]},
            {"node_id": "Final_Course", "credits": 4, "prerequisites": ["Coreq_A", "Coreq_B"]},
        ]
        res_json = self.agent.compute_path(
            "REG1001",
            "Final_Course",
            custom_graph_nodes=custom_nodes
        )
        data = json.loads(res_json)
        self.assertEqual(data["path_status"], STATUS_VALID)

        # Coreq_A and Coreq_B must be scheduled together in step 1
        step_1_nodes = data["path_sequence"][0]["nodes_to_complete"]
        self.assertIn("Coreq_A", step_1_nodes)
        self.assertIn("Coreq_B", step_1_nodes)

    def test_bottleneck_detection(self):
        """Tests detection of critical gateway nodes."""
        target = "Sub_4_15"  # Capstone Project
        res_json = self.agent.compute_path("REG1001", target, completed_nodes=[])
        data = json.loads(res_json)
        self.assertEqual(data["path_status"], STATUS_VALID)
        self.assertIsInstance(data["bottlenecks"], list)


if __name__ == "__main__":
    unittest.main()
