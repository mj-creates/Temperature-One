# Temperature-One

An intelligent multi-agent Academic Advising and Curriculum Management System.

---

## 📁 Repository Structure

```text
Temperature-One/
├── agent-core/             # Multi-agent logic, state synthesizers, schemas, prompts
│   ├── agent_4_background_check.py # Agent 4 (The Background Check / State Synthesizer)
│   ├── nexus.py            # Agent 1 (Front Desk / Supervisor Agent)
│   ├── nexus_prompt.md     # System prompt for Nexus (Agent 01)
│   ├── prompts.py          # System prompt definitions and prompt builders
│   ├── sanitizer.py        # PII & credential scrubbing engine
│   ├── schemas.py          # Pydantic data models & error protocols
│   ├── synthesizer.py      # Zero-hallucination state synthesis engine
│   ├── main.py             # Agent 4 CLI runner & scenario verification
│   ├── test_agent_4.py     # Unit test suite for Agent 4
│   └── README.md           # Agent-core documentation
├── backend/                # FastAPI backend & SQLite database layer
│   ├── database/           # DB connection helpers and module entrypoint
│   ├── init_db.py          # SQLite database schema, rules & mock data initializer
│   ├── main.py             # FastAPI entrypoint (health check & API routes)
│   └── university.db       # SQLite local database
├── frontend/               # React + Vite frontend application
│   ├── src/                # UI components, assets, and styling
│   ├── package.json        # Frontend dependencies & scripts
│   └── vite.config.js      # Vite build configuration
├── automation/             # AI workflow automation & verification scripts
│   └── test.py             # LangChain environment verification
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # Project overview & guide
```

---

## 🚀 Getting Started

### 1. Python Environment & Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize the SQLite Database
python backend/init_db.py

# Run the FastAPI server
uvicorn backend.main:app --reload
```

### 2. Agent Core Execution
```bash
# Run Agent 1 (Nexus Front Desk)
python agent-core/nexus.py

# Run Agent 4 (The Background Check) demo
python agent-core/main.py

# Query a specific student ID
python agent-core/main.py REG1001

# Run Agent 4 Unit Tests
python -m unittest agent-core/test_agent_4.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
