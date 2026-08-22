"""
Compatibility alias module for agent schemas.
"""
try:
    from .agent_schemas import *
except ImportError:
    from agent_schemas import *
