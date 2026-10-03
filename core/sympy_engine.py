"""
Vigyan AI: Safe Symbolic Mathematics & Physics AST Execution Engine
Powered by SymPy for 100% exact algebraic calculus and closed-form derivations.
"""

import ast
from typing import Dict, Any
import sympy as sp

class SymPyEngine:
    def __init__(self):
        self.symbols = {
            'x': sp.Symbol('x'), 'y': sp.Symbol('y'), 'z': sp.Symbol('z'),
            't': sp.Symbol('t'), 's': sp.Symbol('s'), 'n': sp.Symbol('n', integer=True),
            'k': sp.Symbol('k'), 'R': sp.Symbol('R', positive=True),
            'C': sp.Symbol('C', positive=True), 'L': sp.Symbol('L', positive=True),
            'V': sp.Symbol('V'), 'I': sp.Symbol('I'),
            'omega': sp.Symbol('omega', positive=True), 'pi': sp.pi, 'E': sp.E, 'oo': sp.oo
        }
        self.safe_dict = {
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan, 'exp': sp.exp,
            'log': sp.log, 'ln': sp.log, 'sqrt': sp.sqrt, 'diff': sp.diff,
            'integrate': sp.integrate, 'solve': sp.solve, 'linsolve': sp.linsolve,
            'limit': sp.limit, 'series': sp.series, 'simplify': sp.simplify,
            'expand': sp.expand, 'factor': sp.factor, 'dsolve': sp.dsolve,
            'Matrix': sp.Matrix, 'Rational': sp.Rational, 'symbols': sp.symbols,
            'Symbol': sp.Symbol, 'pi': sp.pi, 'e': sp.E, 'oo': sp.oo,
            'abs': sp.Abs, 'factorial': sp.factorial, 'Eq': sp.Eq, 'sp': sp
        }
        self.safe_dict.update(self.symbols)

    def is_safe_code(self, code: str) -> bool:
        """Validates AST to ensure no forbidden operations or imports."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ('eval', 'exec', 'open', '__import__', 'compile', 'globals', 'locals'):
                    return False
        return True

    def evaluate(self, expression_str: str) -> Dict[str, Any]:
        """Evaluates mathematical expression deterministically."""
        code = expression_str.strip()
        for prefix in ["```python", "```"]:
            if code.startswith(prefix):
                code = code[len(prefix):]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        if not self.is_safe_code(code):
            return {"success": False, "error": "Expression contains forbidden syntax or imports."}

        local_scope = dict(self.safe_dict)
        try:
            lines = [l for l in code.split('\n') if l.strip()]
            if len(lines) == 1 and not ('=' in lines[0] and not any(op in lines[0] for op in ['==', '<=', '>='])):
                res = eval(lines[0], {"__builtins__": {}}, local_scope)
            else:
                exec(code, {"__builtins__": {}}, local_scope)
                if 'result' in local_scope:
                    res = local_scope['result']
                elif 'ans' in local_scope:
                    res = local_scope['ans']
                else:
                    assigned = [k for k in local_scope.keys() if k not in self.safe_dict and not k.startswith('_')]
                    res = local_scope[assigned[-1]] if assigned else "OK"

            latex_str = sp.latex(res) if isinstance(res, (sp.Basic, sp.Matrix)) else str(res)
            num_approx = None
            if isinstance(res, (sp.Basic, sp.Matrix)):
                try:
                    if hasattr(res, 'evalf') and not res.free_symbols:
                        val = res.evalf(6)
                        num_approx = float(val) if val.is_real else str(val)
                except Exception:
                    pass
            elif isinstance(res, (int, float)):
                num_approx = float(res)

            return {
                "success": True,
                "result": str(res),
                "latex": latex_str,
                "numeric_approx": num_approx
            }
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {str(e)}"}
