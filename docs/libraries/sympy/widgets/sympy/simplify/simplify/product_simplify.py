"""
SymPy product_simplify Widget
Main function for Product simplification
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import product_simplify


class SymPyProduct_SimplifyWidget:
    """Widget for SymPy product_simplify function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the product_simplify function."""
        try:
            # Extract parameters from input
            s = validated_input.get('s', None)
            kwargs = validated_input.get('kwargs', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['s', 'kwargs'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = product_simplify(s, kwargs)
            
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
                    'function': 'product_simplify',
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
                    'function': 'product_simplify',
                    'module': 'sympy.simplify.simplify'
                }
            }
