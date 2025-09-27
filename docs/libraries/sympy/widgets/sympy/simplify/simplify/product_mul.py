"""
SymPy product_mul Widget
Helper function for Product simplification
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import product_mul


class SymPyProduct_MulWidget:
    """Widget for SymPy product_mul function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the product_mul function."""
        try:
            # Extract parameters from input
            self = validated_input.get('self', None)
            other = validated_input.get('other', None)
            method = validated_input.get('method', '0')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['self', 'other', 'method'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = product_mul(self, other, method)
            
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
                    'function': 'product_mul',
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
                    'function': 'product_mul',
                    'module': 'sympy.simplify.simplify'
                }
            }
