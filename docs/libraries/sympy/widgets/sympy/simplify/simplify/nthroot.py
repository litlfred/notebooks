"""
SymPy nthroot Widget
Compute a real nth-root of a sum of surds.
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import nthroot


class SymPyNthrootWidget:
    """Widget for SymPy nthroot function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the nthroot function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            n = validated_input.get('n', None)
            max_len = validated_input.get('max_len', '4')
            prec = validated_input.get('prec', '15')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'n', 'max_len', 'prec'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = nthroot(expr, n, max_len, prec)
            
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
                    'function': 'nthroot',
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
                    'function': 'nthroot',
                    'module': 'sympy.simplify.simplify'
                }
            }
