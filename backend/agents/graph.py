import sys
import os
import logging
from typing import TypedDict, Optional, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import run_research_agent
from agents.critic_agent import run_critic_agent
from agents.supervisor_agent import run_supervisor_agent

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


# ── State Definition ──────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    Shared state passed between all three agents.
    Each agent reads from and writes to this state dict.
    """
    query:                str
    domain:               str

    # Agent 1 output
    research_answer:      Optional[dict]

    # Agent 2 output
    critic_report:        Optional[dict]

    # Agent 3 output (shown to user)
    final_answer:         Optional[dict]

    # Pipeline metadata
    error:                Optional[str]
    processing_steps:     list[str]       # Tracks which agents ran (for UI pills)


# ── Node Functions ────────────────────────────────────────────────────────────

def research_node(state: AgentState) -> AgentState:
    """Agent 1: Fetch regulatory data and generate initial answer."""
    logger.info("Graph: research_node started")

    try:
        answer = run_research_agent(
            query=state["query"],
            domain=state["domain"],
        )
        return {
            **state,
            "research_answer": answer,
            "processing_steps": state.get("processing_steps", []) + ["Research Agent ✓"],
        }
    except Exception as e:
        logger.error(f"research_node error: {e}")
        return {
            **state,
            "research_answer": None,
            "error": f"Research Agent failed: {str(e)}",
            "processing_steps": state.get("processing_steps", []) + ["Research Agent ✗"],
        }


def critic_node(state: AgentState) -> AgentState:
    """Agent 2: Verify and critique the research answer (LLM as Judge)."""
    logger.info("Graph: critic_node started")

    if state.get("error") or state.get("research_answer") is None:
        return {
            **state,
            "critic_report": {"overall_verdict": "REJECT", "revision_instructions": "Research failed."},
            "processing_steps": state.get("processing_steps", []) + ["Critic Agent ✗"],
        }

    try:
        critique = run_critic_agent(
            user_query=state["query"],
            domain=state["domain"],
            agent1_answer=state["research_answer"],
        )
        return {
            **state,
            "critic_report": critique,
            "processing_steps": state.get("processing_steps", []) + ["Critic Agent ✓"],
        }
    except Exception as e:
        logger.error(f"critic_node error: {e}")
        return {
            **state,
            "critic_report": {
                "overall_verdict": "REVISE",
                "revision_instructions": f"Critic error: {str(e)}",
            },
            "processing_steps": state.get("processing_steps", []) + ["Critic Agent ✗"],
        }


def supervisor_node(state: AgentState) -> AgentState:
    """Agent 3: Synthesize final answer with confidence score."""
    logger.info("Graph: supervisor_node started")

    if state.get("error") and state.get("research_answer") is None:
        final = {
            "final_answer": "Unable to process your query due to an error. Please try again.",
            "confidence_level": "LOW",
            "confidence_score": 0.0,
            "confidence_explanation": state.get("error", "Unknown error"),
            "deadlines": [],
            "domain": state["domain"],
        }
        return {
            **state,
            "final_answer": final,
            "processing_steps": state.get("processing_steps", []) + ["Supervisor ✗"],
        }

    try:
        final = run_supervisor_agent(
            user_query=state["query"],
            domain=state["domain"],
            agent1_answer=state.get("research_answer", {}),
            critic_report=state.get("critic_report", {}),
        )
        return {
            **state,
            "final_answer": final,
            "processing_steps": state.get("processing_steps", []) + ["Supervisor Verified ✓"],
        }
    except Exception as e:
        logger.error(f"supervisor_node error: {e}")
        return {
            **state,
            "final_answer": {
                "final_answer": "Supervisor Agent failed. Please retry.",
                "confidence_level": "LOW",
                "confidence_score": 0.0,
                "confidence_explanation": str(e),
                "deadlines": [],
                "domain": state["domain"],
            },
            "processing_steps": state.get("processing_steps", []) + ["Supervisor ✗"],
        }


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> Any:
    """
    Constructs the LangGraph state machine.
    Returns a compiled graph ready to invoke.
    """
    builder = StateGraph(AgentState)

    # Add the three agent nodes
    builder.add_node("research", research_node)
    builder.add_node("critic", critic_node)
    builder.add_node("supervisor", supervisor_node)

    # Define the linear flow: research → critic → supervisor → END
    builder.set_entry_point("research")
    builder.add_edge("research", "critic")
    builder.add_edge("critic", "supervisor")
    builder.add_edge("supervisor", END)

    return builder.compile()


fincomply_graph = build_graph()


def run_pipeline(query: str, domain: str) -> dict:
    """
    Run the full 3-agent pipeline and return the final answer.
    This is the only function api/main.py needs to call.
    """
    initial_state: AgentState = {
        "query": query,
        "domain": domain,
        "research_answer": None,
        "critic_report": None,
        "final_answer": None,
        "error": None,
        "processing_steps": [],
    }

    result = fincomply_graph.invoke(initial_state)

    return {
        "answer": result.get("final_answer", {}),
        "processing_steps": result.get("processing_steps", []),
        "domain": domain,
        "query": query,
    }