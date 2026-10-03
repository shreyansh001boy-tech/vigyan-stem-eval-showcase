"""
Vigyan AI: Native Sovereign Agent
Decoupled Intent Router + Deterministic Symbolic Math + C++ GraphRAG.
Supports 2B Edge, 7B Workhorse, and 32B Titan model backends.
"""

import os
import sys
import time
from typing import Dict, Any, Optional

from core.sympy_engine import SymPyEngine
from core.kuzu_graph import KuzuSTEMGraph

class VigyanAgent:
    def __init__(self, model_tier: str = "7b", local_llm=None, tokenizer=None):
        self.model_tier = model_tier.lower()
        self.math_engine = SymPyEngine()
        self.graph = KuzuSTEMGraph()
        self.llm = local_llm
        self.tokenizer = tokenizer

    def answer(self, prompt: str) -> Dict[str, Any]:
        p_lower = prompt.strip().lower()

        # 1. Fast-Path: Small Talk & Conversational Fluency (0.0001s)
        greetings = ["hi", "hii", "hello", "hey", "namaste", "good morning", "good evening", "thanks", "thank you"]
        if p_lower in greetings or any(p_lower.startswith(g) for g in ["hi ", "hello ", "hey "]):
            return {
                "intent": "conversational_fastpath",
                "latency_s": 0.0001,
                "tool_used": None,
                "response": "Hello! I am Vigyan AI, your sovereign neuro-symbolic assistant for STEM, circuits, physics, and calculus. How can I assist your derivations today?"
            }

        # 2. Fast-Path: Exact Calculus & Closed-Form Derivations
        math_triggers = ["integrate ", "derivative of ", "solve ", "calculate ", "diff(", "int("]
        for tr in math_triggers:
            if p_lower.startswith(tr):
                t0 = time.time()
                expr = prompt[len(tr):].strip()
                if tr == "derivative of ":
                    clean_expr = f"diff({expr}, x)" if ' x' not in expr and not expr.endswith('x') else expr
                elif tr == "integrate ":
                    clean_expr = f"integrate({expr})" if '(' not in expr else expr
                else:
                    clean_expr = expr

                res = self.math_engine.evaluate(clean_expr)
                lat = round(time.time() - t0, 4)
                if res.get("success"):
                    resp = f"**Exact Closed-Form Solution:**\n$${res.get('latex')}$$\n\nSymbolic Expression: `{res.get('result')}`"
                    if res.get("numeric_approx") is not None:
                        resp += f"\nNumeric Approximation: `{res.get('numeric_approx')}`"
                    return {
                        "intent": "symbolic_calculus_fastpath",
                        "latency_s": lat,
                        "tool_used": "sympy",
                        "response": resp
                    }

        # 3. Grounding: C++ GraphRAG Context Retrieval
        t0 = time.time()
        words = [w for w in p_lower.replace("?", "").replace(",", "").split() if len(w) > 3]
        graph_context = self.graph.query_multihop_context(words)

        if self.llm is None or self.tokenizer is None:
            # CPU / Local Tool Fallback
            lat = round(time.time() - t0, 4)
            if graph_context:
                resp = f"**Verified Causal Axioms from KùzuDB GraphRAG:**\n\n{graph_context}\n\n*Note: Running in CPU grounding mode. Connect a GPU model tier for full parametric synthesis.*"
            else:
                resp = f"Vigyan AI received query: '{prompt}'. No exact closed-form calculus trigger matched. Connect model weights for neural synthesis."
            return {
                "intent": "graphrag_grounded_fallback",
                "latency_s": lat,
                "tool_used": "kuzu_graph" if graph_context else None,
                "response": resp
            }

        # 4. Full GPU Neural Generation
        import torch
        sys_prompt = "You are Vigyan AI, a sovereign, rigorous, and highly concise STEM research assistant. Provide mathematically precise and pedagogically clear explanations."
        augmented_user = f"{prompt}\n\n[Verified Physical Axioms from KùzuDB]:\n{graph_context}" if graph_context else prompt
        full_prompt = f"<|system|>\n{sys_prompt}\n<|user|>\n{augmented_user}\n<|assistant|>\n"
        
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.llm.device)
        with torch.no_grad():
            outputs = self.llm.generate(
                **inputs,
                max_new_tokens=384,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        gen = outputs[0][inputs["input_ids"].shape[1]:]
        resp = self.tokenizer.decode(gen, skip_special_tokens=True).strip()
        lat = round(time.time() - t0, 4)

        return {
            "intent": "neuro_symbolic_synthesis",
            "latency_s": lat,
            "tool_used": "kuzu_graph" if graph_context else None,
            "response": resp
        }
