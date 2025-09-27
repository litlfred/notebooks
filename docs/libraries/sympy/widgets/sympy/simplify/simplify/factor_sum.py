"""
SymPy factor_sum Widget
Return Sum with constant factors extracted. If ``limits`` is specified then ``self`` is the summand; the other keywords are passed to ``factor_terms``. Examples >>> from sympy import Sum >>> from sympy.abc import x, y >>> from sympy.simplify.simplify import factor_sum >>> s = Sum(x*y, (x, 1, 3)) >>> factor_sum(s) y*Sum(x, (x, 1, 3)) >>> factor_sum(s.function, s.limits) y*Sum(x, (x, 1, 3))
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import factor_sum


class SymPyFactor_SumWidget:
    """Widget for SymPy factor_sum function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the factor_sum function."""
        try:
            # Extract parameters from input
            self = validated_input.get('self', None)
            limits = validated_input.get('limits', 'None')
            radical = validated_input.get('radical', 'False')
            clear = validated_input.get('clear', 'False')
            fraction = validated_input.get('fraction', 'False')
            sign = validated_input.get('sign', 'True')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['self', 'limits', 'radical', 'clear', 'fraction', 'sign'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = factor_sum(self, limits, radical, clear, fraction, sign)
            
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
                    'function': 'factor_sum',
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
                    'function': 'factor_sum',
                    'module': 'sympy.simplify.simplify'
                }
            }
