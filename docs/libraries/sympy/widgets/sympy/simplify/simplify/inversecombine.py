"""
SymPy inversecombine Widget
Simplify the composition of a function and its inverse. Explanation No attention is paid to whether the inverse is a left inverse or a right inverse; thus, the result will in general not be equivalent to the original expression. Examples >>> from sympy.simplify.simplify import inversecombine >>> from sympy import asin, sin, log, exp >>> from sympy.abc import x >>> inversecombine(asin(sin(x))) x >>> inversecombine(2*log(exp(3*x))) 6*x
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import inversecombine


class SymPyInversecombineWidget:
    """Widget for SymPy inversecombine function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the inversecombine function."""
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
            result = inversecombine(expr)
            
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
                    'function': 'inversecombine',
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
                    'function': 'inversecombine',
                    'module': 'sympy.simplify.simplify'
                }
            }
