"""
Vigyan AI: Hugging Face smolagents (CodeAgent) Comparison Adapter
Exposes KùzuDB and SymPy as @tools for side-by-side agentic evaluation.
"""

import os
import sys
import time
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.sympy_engine import SymPyEngine
from core.kuzu_graph import KuzuSTEMGraph

try:
    from smolagents import tool, CodeAgent
except ImportError:
    pass

_math = SymPyEngine()
_graph = KuzuSTEMGraph()

try:
    @tool
    def sympy_math_solver(expression: str) -> str:
        """
        Evaluates mathematical expressions, derivatives, integrals, and equations using SymPy.
        Args:
            expression: The math expression to evaluate (e.g. 'diff(x**3, x)').
        """
        res = _math.evaluate(expression)
        if res.get("success"):
            return f"Exact Result: {res.get('result')}\nLaTeX: {res.get('latex')}"
        return f"Error: {res.get('error')}"

    @tool
    def kuzu_knowledge_graph_query(keyword: str) -> str:
        """
        Queries KùzuDB C++ graph for physical laws, circuit constants, and semiconductor axioms.
        Args:
            keyword: The entity or concept keyword (e.g. 'MOSFET', 'Vis-Viva').
        """
        facts = _graph.query_multihop_context([keyword])
        return facts if facts else f"No axiom found for '{keyword}'."
except Exception:
    pass

def get_smolagent(model=None):
    """Instantiates a CodeAgent with STEM tools."""
    from smolagents import CodeAgent
    return CodeAgent(
        tools=[sympy_math_solver, kuzu_knowledge_graph_query],
        model=model,
        max_steps=3
    )
