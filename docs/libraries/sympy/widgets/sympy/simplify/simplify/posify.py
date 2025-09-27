"""
SymPy posify Widget
Return ``eq`` (with generic symbols made positive) and a dictionary containing the mapping between the old and new symbols. Explanation Any symbol that has positive=None will be replaced with a positive dummy symbol having the same name. This replacement will allow more symbolic processing of expressions, especially those involving powers and logarithms. A dictionary that can be sent to subs to restore ``eq`` to its original symbols is also returned. >>> from sympy import posify, Symbol, log, solve >>> from sympy.abc import x >>> posify(x + Symbol('p', positive=True) + Symbol('n', negative=True)) (_x + n + p, {_x: x}) >>> eq = 1/x >>> log(eq).expand() log(1/x) >>> log(posify(eq)[0]).expand() -log(_x) >>> p, rep = posify(eq) >>> log(p).expand().subs(rep) -log(x) It is possible to apply the same transformations to an iterable of expressions: >>> eq = x**2 - 4 >>> solve(eq, x) [-2, 2] >>> eq_x, reps = posify([eq, x]); eq_x [_x**2 - 4, _x] >>> solve(*eq_x) [2]
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import posify


class SymPyPosifyWidget:
    """Widget for SymPy posify function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the posify function."""
        try:
            # Extract parameters from input
            eq = validated_input.get('eq', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['eq'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = posify(eq)
            
            # Format output
            result_str = str(result)
            try:
                latex_str = sp.latex(result) if hasattr(result, '_latex') or hasattr(sp, 'latex') else result_str
            except:
                latex_str = result_str
            
            return {
                'result': result_str,
                'latex': latex_str,
                'metadata': {
                    'function': 'posify',
                    'module': 'sympy.simplify.simplify',
                    'result_type': type(result).__name__,
                    'parameters_used': validated_input
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'function': 'posify',
                    'module': 'sympy.simplify.simplify'
                }
            }
