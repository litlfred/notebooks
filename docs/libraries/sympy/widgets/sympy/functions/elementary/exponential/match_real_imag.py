"""
SymPy match_real_imag Widget
Try to match expr with $a + Ib$ for real $a$ and $b$. ``match_real_imag`` returns a tuple containing the real and imaginary parts of expr or ``(None, None)`` if direct matching is not possible. Contrary to :func:`~.re`, :func:`~.im``, and ``as_real_imag()``, this helper will not force things by returning expressions themselves containing ``re()`` or ``im()`` and it does not expand its argument either.
"""

from typing import Dict, Any
import sympy as sp
from sympy.functions.elementary.exponential import match_real_imag


class SymPyMatch_Real_ImagWidget:
    """Widget for SymPy match_real_imag function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the match_real_imag function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = match_real_imag(expr)
            
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
                    'function': 'match_real_imag',
                    'module': 'sympy.functions.elementary.exponential',
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
                    'function': 'match_real_imag',
                    'module': 'sympy.functions.elementary.exponential'
                }
            }
