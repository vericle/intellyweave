# ABOUTME: Courthouse debate system for multi-agent deliberation on query responses
# ABOUTME: Exports the main CourthouseDebate tool and agent implementations

from .courthouse_debate import CourthouseDebate
from .judge_agent import JudgeAgent
from .defense_agent import DefenseAgent
from .prosecution_agent import ProsecutionAgent

__all__ = [
    "CourthouseDebate",
    "JudgeAgent",
    "DefenseAgent",
    "ProsecutionAgent",
]