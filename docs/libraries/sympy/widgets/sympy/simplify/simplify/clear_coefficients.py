"""
SymPy clear_coefficients Widget
Return `p, r` where `p` is the expression obtained when Rational additive and multiplicative coefficients of `expr` have been stripped away in a naive fashion (i.e. without simplification). The operations needed to remove the coefficients will be applied to `rhs` and returned as `r`. Examples >>> from sympy.simplify.simplify import clear_coefficients >>> from sympy.abc import x, y >>> from sympy import Dummy >>> expr = 4*y*(6*x + 3) >>> clear_coefficients(expr - 2) (y*(2*x + 1), 1/6) When solving 2 or more expressions like `expr = a`, `expr = b`, etc..., it is advantageous to provide a Dummy symbol for `rhs` and  simply replace it with `a`, `b`, etc... in `r`. >>> rhs = Dummy('rhs') >>> clear_coefficients(expr, rhs) (y*(2*x + 1), _rhs/12) >>> _[1].subs(rhs, 2) 1/6
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import clear_coefficients


class SymPyClear_CoefficientsWidget:
    """Widget for SymPy clear_coefficients function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the clear_coefficients function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            rhs = validated_input.get('rhs', '0')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'rhs'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = clear_coefficients(expr, rhs)
            
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
                    'function': 'clear_coefficients',
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
                    'function': 'clear_coefficients',
                    'module': 'sympy.simplify.simplify'
                }
            }
