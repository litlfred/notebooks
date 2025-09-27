"""
SymPy signsimp Widget
Make all Add sub-expressions canonical wrt sign. Explanation If an Add subexpression, ``a``, can have a sign extracted, as determined by could_extract_minus_sign, it is replaced with Mul(-1, a, evaluate=False). This allows signs to be extracted from powers and products. Examples >>> from sympy import signsimp, exp, symbols >>> from sympy.abc import x, y >>> i = symbols('i', odd=True) >>> n = -1 + 1/x >>> n/x/(-n)**2 - 1/n/x (-1 + 1/x)/(x*(1 - 1/x)**2) - 1/(x*(-1 + 1/x)) >>> signsimp(_) 0 >>> x*n + x*-n x*(-1 + 1/x) + x*(1 - 1/x) >>> signsimp(_) 0 Since powers automatically handle leading signs >>> (-2)**i -2**i signsimp can be used to put the base of a power with an integer exponent into canonical form: >>> n**i (-1 + 1/x)**i By default, signsimp does not leave behind any hollow simplification: if making an Add canonical wrt sign didn't change the expression, the original Add is restored. If this is not desired then the keyword ``evaluate`` can be set to False: >>> e = exp(y - x) >>> signsimp(e) == e True >>> signsimp(e, evaluate=False) exp(-(x - y))
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import signsimp


class SymPySignsimpWidget:
    """Widget for SymPy signsimp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the signsimp function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            evaluate = validated_input.get('evaluate', 'None')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'evaluate'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = signsimp(expr, evaluate)
            
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
                    'function': 'signsimp',
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
                    'function': 'signsimp',
                    'module': 'sympy.simplify.simplify'
                }
            }
