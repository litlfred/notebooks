"""
SymPy expand_mul Widget
Wrapper around expand that only uses the mul hint.  See the expand docstring for more information. Examples >>> from sympy import symbols, expand_mul, exp, log >>> x, y = symbols('x,y', positive=True) >>> expand_mul(exp(x+y)*(x+y)*log(x*y**2)) x*exp(x + y)*log(x*y**2) + y*exp(x + y)*log(x*y**2)
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import expand_mul


class SymPyExpand_MulWidget:
    """Widget for SymPy expand_mul function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the expand_mul function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            deep = validated_input.get('deep', 'True')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'deep'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = expand_mul(expr, deep)
            
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
                    'function': 'expand_mul',
                    'module': 'sympy.core.function',
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
                    'function': 'expand_mul',
                    'module': 'sympy.core.function'
                }
            }
