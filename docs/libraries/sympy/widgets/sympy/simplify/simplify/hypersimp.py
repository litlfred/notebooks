"""
SymPy hypersimp Widget
Given combinatorial term f(k) simplify its consecutive term ratio i.e. f(k+1)/f(k).  The input term can be composed of functions and integer sequences which have equivalent representation in terms of gamma special function. Explanation The algorithm performs three basic steps: 1. Rewrite all functions in terms of gamma, if possible. 2. Rewrite all occurrences of gamma in terms of products of gamma and rising factorial with integer,  absolute constant exponent. 3. Perform simplification of nested fractions, powers and if the resulting expression is a quotient of polynomials, reduce their total degree. If f(k) is hypergeometric then as result we arrive with a quotient of polynomials of minimal degree. Otherwise None is returned. For more information on the implemented algorithm refer to: 1. W. Koepf, Algorithms for m-fold Hypergeometric Summation, Journal of Symbolic Computation (1995) 20, 399-417
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import hypersimp


class SymPyHypersimpWidget:
    """Widget for SymPy hypersimp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the hypersimp function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            k = validated_input.get('k', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'k'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = hypersimp(f, k)
            
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
                    'function': 'hypersimp',
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
                    'function': 'hypersimp',
                    'module': 'sympy.simplify.simplify'
                }
            }
