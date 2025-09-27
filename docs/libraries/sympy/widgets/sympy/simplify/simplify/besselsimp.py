"""
SymPy besselsimp Widget
Simplify bessel-type functions. Explanation This routine tries to simplify bessel-type functions. Currently it only works on the Bessel J and I functions, however. It works by looking at all such functions in turn, and eliminating factors of "I" and "-1" (actually their polar equivalents) in front of the argument. Then, functions of half-integer order are rewritten using trigonometric functions and functions of integer order (> 1) are rewritten using functions of low order.  Finally, if the expression was changed, compute factorization of the result with factor(). >>> from sympy import besselj, besseli, besselsimp, polar_lift, I, S >>> from sympy.abc import z, nu >>> besselsimp(besselj(nu, z*polar_lift(-1))) exp(I*pi*nu)*besselj(nu, z) >>> besselsimp(besseli(nu, z*polar_lift(-I))) exp(-I*pi*nu/2)*besselj(nu, z) >>> besselsimp(besseli(S(-1)/2, z)) sqrt(2)*cosh(z)/(sqrt(pi)*sqrt(z)) >>> besselsimp(z*besseli(0, z) + z*(besseli(2, z))/2 + besseli(1, z)) 3*z*besseli(0, z)/2
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import besselsimp


class SymPyBesselsimpWidget:
    """Widget for SymPy besselsimp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the besselsimp function."""
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
            result = besselsimp(expr)
            
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
                    'function': 'besselsimp',
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
                    'function': 'besselsimp',
                    'module': 'sympy.simplify.simplify'
                }
            }
