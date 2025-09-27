"""
SymPy assume_integer_order Widget
SymPy assume_integer_order function
"""

from typing import Dict, Any
import sympy as sp
from sympy.functions.special.bessel import assume_integer_order


class SymPyAssume_Integer_OrderWidget:
    """Widget for SymPy assume_integer_order function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the assume_integer_order function."""
        try:
            # Extract parameters from input
            fn = validated_input.get('fn', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['fn'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = assume_integer_order(fn)
            
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
                    'function': 'assume_integer_order',
                    'module': 'sympy.functions.special.bessel',
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
                    'function': 'assume_integer_order',
                    'module': 'sympy.functions.special.bessel'
                }
            }
