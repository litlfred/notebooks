"""
SymPy nfloat Widget
Make all Rationals in expr Floats except those in exponents (unless the exponents flag is set to True) and those in undefined functions. When processing dictionaries, do not modify the keys unless ``dkeys=True``. Examples >>> from sympy import nfloat, cos, pi, sqrt >>> from sympy.abc import x, y >>> nfloat(x**4 + x/2 + cos(pi/3) + 1 + sqrt(y)) x**4 + 0.5*x + sqrt(y) + 1.5 >>> nfloat(x**4 + sqrt(y), exponent=True) x**4.0 + y**0.5 Container types are not modified: >>> type(nfloat((1, 2))) is tuple True
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import nfloat


class SymPyNfloatWidget:
    """Widget for SymPy nfloat function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the nfloat function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            n = validated_input.get('n', '15')
            exponent = validated_input.get('exponent', 'False')
            dkeys = validated_input.get('dkeys', 'False')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'n', 'exponent', 'dkeys'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = nfloat(expr, n, exponent, dkeys)
            
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
                    'function': 'nfloat',
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
                    'function': 'nfloat',
                    'module': 'sympy.core.function'
                }
            }
