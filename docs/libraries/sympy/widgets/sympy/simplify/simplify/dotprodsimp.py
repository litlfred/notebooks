"""
SymPy dotprodsimp Widget
Simplification for a sum of products targeted at the kind of blowup that occurs during summation of products. Intended to reduce expression blowup during matrix multiplication or other similar operations. Only works with algebraic expressions and does not recurse into non.
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import dotprodsimp


class SymPyDotprodsimpWidget:
    """Widget for SymPy dotprodsimp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the dotprodsimp function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            withsimp = validated_input.get('withsimp', False)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'withsimp'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = dotprodsimp(expr, withsimp)
            
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
                    'function': 'dotprodsimp',
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
                    'function': 'dotprodsimp',
                    'module': 'sympy.simplify.simplify'
                }
            }
