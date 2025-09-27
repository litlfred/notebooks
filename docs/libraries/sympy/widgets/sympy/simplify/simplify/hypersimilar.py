"""
SymPy hypersimilar Widget
Returns True if ``f`` and ``g`` are hyper-similar. Explanation Similarity in hypergeometric sense means that a quotient of f(k) and g(k) is a rational function in ``k``. This procedure is useful in solving recurrence relations. For more information see hypersimp().
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import hypersimilar


class SymPyHypersimilarWidget:
    """Widget for SymPy hypersimilar function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the hypersimilar function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            g = validated_input.get('g', None)
            k = validated_input.get('k', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'g', 'k'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = hypersimilar(f, g, k)
            
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
                    'function': 'hypersimilar',
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
                    'function': 'hypersimilar',
                    'module': 'sympy.simplify.simplify'
                }
            }
