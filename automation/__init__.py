"""
Automation package for AI workflows, automated testing, and multi-agent pipeline orchestration.
"""

from .orchestrator import (
    run_advising,
    call_nexus,
    call_state,
    call_codex,
    call_matrix,
    call_vector,
)

__all__ = [
    "run_advising",
    "call_nexus",
    "call_state",
    "call_codex",
    "call_matrix",
    "call_vector",
]
