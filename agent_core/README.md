# Agent Core: System Architecture & Multi-Agent Pipeline

This package houses the autonomous agent logic, synthesis engines, graph navigators, and schemas for the Anti Gravity pipeline.

---

## 🤖 Agents Overview

```
[Student Input]
      │
      ▼
┌──────────────┐
│ Agent 1:     │ (Nexus / Front Desk)
│ Nexus        │ ──▶ Greet student & collect academic/career goals
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Agent 4:     │ (State Synthesizer / Background Check)
│ State        │ ──▶ Inspect DBMS, verify standing, sanitize records, output Student State JSON
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Agent 2:     │ (Graph Navigator & Pathfinder)
│ The Matrix   │ ──▶ Compute conflict-free, optimal chronological pathway to target node/goal
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Agent 3:     │ (Career & Certification Advisor)
│ Vector       │ ──▶ Provide actionable career, certification & internship pathways
└──────────────┘
```

---

## Agent 2: "The Matrix" (Graph Navigator & Pathfinder)

### 1. Core Mission
Agent 2 navigates complex curriculum and skill graphs, calculates critical paths, resolves prerequisite webs, and outputs a validated, chronological sequence to reach the target course or degree milestone.

### 2. Operational Guardrails
- **Zero-Tolerance Hallucination**: Only maps paths using exact node IDs and names provided in the graph or catalog.
- **Strict Temporal Logic**: Prerequisites scheduled prior; co-requisites scheduled in the same (or prior) step; anti-requisites excluded.
- **State Awareness**: Never re-schedules completed courses from the student's profile.
- **Load Optimization**: Balances credits/effort across sequence steps (terms/semesters) up to credit limits (e.g., 20 credits/step).

### 3. Error & Impasse Protocols
- **Unreachable Target**: `{"status": "PATH_UNREACHABLE", "error": "MISSING_CRITICAL_NODE", "sequence": []}`
- **Cyclic Dependency**: `{"status": "GRAPH_ERROR", "error": "CYCLIC_DEPENDENCY", "sequence": []}`
- **Target Already Completed**: `{"status": "ALREADY_ACHIEVED", "error": null, "sequence": []}`

### 4. Output JSON Schema
```json
{
  "student_id": "string",
  "target_node": "string",
  "path_status": "string (e.g., VALID, UNREACHABLE, ALREADY_ACHIEVED)",
  "total_steps_required": "integer",
  "path_sequence": [
    {
      "step_number": "integer",
      "step_label": "string (e.g., Term 1, Sprint A)",
      "nodes_to_complete": ["array of exact node IDs"],
      "step_total_credits_or_effort": "number"
    }
  ],
  "bottlenecks": ["array of node IDs that act as critical chokepoints/gateways"],
  "matrix_analysis": "A strict, 2-sentence logical proof explaining why this path is the most optimal route and confirming all prerequisites are satisfied."
}
```

---

## Agent 4: "The Background Check" (State Synthesizer)

### 1. Core Mission
Inspects raw student records from the backend DBMS, evaluates operational and academic standing, and outputs validated "Student State" JSON.

### 2. Operational Guardrails & Sanitization
- Zero-tolerance hallucination (missing fields output as explicit `null` / `[]`).
- Strips passwords, hashes, tokens, API keys, and banking data.
- Read-only database access.

---

## Quick Usage

### Programmatic API
```python
from agent_core import MatrixAgent, Agent4BackgroundCheck, run_matrix, run_agent_4

# 1. State Synthesis (Agent 4)
agent_4 = Agent4BackgroundCheck()
state_json = agent_4.inspect_student_id("REG1001")

# 2. Pathfinding (The Matrix / Agent 2)
matrix = MatrixAgent()
# Compute path to Deep Learning (Sub_4_2)
path_json = matrix.compute_path(student_id="REG1001", target_node="Sub_4_2")
print(path_json)
```

### CLI Execution
```bash
# Run multi-agent demonstration harness
python agent_core/main.py

# Run Matrix pathfinder for a specific course
python agent_core/matrix.py Sub_4_2 REG1001

# Run unit tests
python -m unittest agent_core/test_matrix.py
python -m unittest agent_core/test_agent_4.py
```
