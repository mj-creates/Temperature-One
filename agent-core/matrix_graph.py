"""
Matrix Graph Engine: Graph representation, cycle detection, topological sorting,
and constraint-aware pathfinding for the Anti Gravity autonomous pipeline.
"""

from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional, Any


class GraphNode:
    """Represents a node in the prerequisite graph."""
    def __init__(
        self,
        node_id: str,
        name: str = "",
        credits: float = 3.0,
        semester: Optional[int] = None,
        prerequisites: Optional[List[str]] = None,
        corequisites: Optional[List[str]] = None,
        antirequisites: Optional[List[str]] = None,
    ):
        self.node_id = str(node_id).strip()
        self.name = name or self.node_id
        self.credits = float(credits)
        self.semester = semester
        self.prerequisites: List[str] = [str(p).strip() for p in (prerequisites or [])]
        self.corequisites: List[str] = [str(c).strip() for c in (corequisites or [])]
        self.antirequisites: List[str] = [str(a).strip() for a in (antirequisites or [])]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "credits": self.credits,
            "semester": self.semester,
            "prerequisites": self.prerequisites,
            "corequisites": self.corequisites,
            "antirequisites": self.antirequisites,
        }


class PrerequisiteGraph:
    """
    Manages graph topology, validates temporal constraints, and computes
    conflict-free sequences.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def detect_cycles(self, target_nodes: Optional[Set[str]] = None) -> Optional[List[str]]:
        """
        Detects if there is any cyclic dependency in the graph (or subgraph leading to targets).
        Returns the cycle path as list of node IDs if found, otherwise None.
        """
        subgraph_nodes = target_nodes if target_nodes is not None else set(self.nodes.keys())
        
        visited: Dict[str, int] = {}  # 0: unvisited, 1: visiting (in recursion stack), 2: visited
        parent_map: Dict[str, str] = {}
        cycle: List[str] = []

        def dfs(u: str) -> bool:
            visited[u] = 1
            node = self.nodes.get(u)
            if node:
                for prereq in node.prerequisites:
                    if prereq not in subgraph_nodes or prereq not in self.nodes:
                        continue
                    if visited.get(prereq, 0) == 1:
                        # Cycle found!
                        cycle.append(prereq)
                        curr = u
                        while curr != prereq and curr in parent_map:
                            cycle.append(curr)
                            curr = parent_map[curr]
                        cycle.append(prereq)
                        cycle.reverse()
                        return True
                    elif visited.get(prereq, 0) == 0:
                        parent_map[prereq] = u
                        if dfs(prereq):
                            return True
            visited[u] = 2
            return False

        for node_id in subgraph_nodes:
            if visited.get(node_id, 0) == 0:
                if dfs(node_id):
                    return cycle
        return None

    def get_required_subgraph(
        self,
        target_node: str,
        completed_nodes: Set[str]
    ) -> Tuple[Optional[Set[str]], Optional[str]]:
        """
        Computes all ancestor prerequisite nodes needed to reach target_node.
        Returns (set_of_all_required_nodes, missing_node_id_if_unreachable).
        """
        if target_node not in self.nodes:
            return None, target_node

        required: Set[str] = set()
        queue = deque([target_node])
        visited = set()

        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)
            required.add(curr)

            node = self.nodes.get(curr)
            if not node:
                # Missing critical node from graph that isn't completed
                if curr not in completed_nodes:
                    return None, curr
                continue

            # Check prerequisites
            for p in node.prerequisites:
                if p not in self.nodes and p not in completed_nodes:
                    return None, p
                if p not in visited and p not in completed_nodes:
                    queue.append(p)

            # Check corequisites
            for c in node.corequisites:
                if c not in self.nodes and c not in completed_nodes:
                    return None, c
                if c not in visited and c not in completed_nodes:
                    queue.append(c)

        return required, None

    def identify_bottlenecks(self, required_nodes: Set[str], target_node: str) -> List[str]:
        """
        Identifies critical chokepoints / gateway nodes in the prerequisite path.
        A node is a bottleneck if multiple downstream courses depend on it or it sits on all critical paths.
        """
        dependent_count: Dict[str, int] = defaultdict(int)
        for nid in required_nodes:
            node = self.nodes.get(nid)
            if not node:
                continue
            for p in node.prerequisites:
                if p in required_nodes:
                    dependent_count[p] += 1

        # Nodes with high fan-out (>= 2 dependents) or required directly on target path
        bottlenecks = [
            nid for nid, count in dependent_count.items()
            if count >= 2 and nid != target_node
        ]
        
        # Sort bottlenecks by graph depth/semester
        bottlenecks.sort(key=lambda nid: (self.nodes[nid].semester or 0, nid))
        return bottlenecks
