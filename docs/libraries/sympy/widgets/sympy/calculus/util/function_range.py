"""
SymPy function_range Widget
Finds the range of a function in a given domain. This method is limited by the ability to determine the singularities and determine limits.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.util import function_range


class SymPyFunction_RangeWidget:
    """Widget for SymPy function_range function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the function_range function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            symbol = validated_input.get('symbol', None)
            domain = validated_input.get('domain', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'symbol', 'domain'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = function_range(f, symbol, domain)
            
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
                    'function': 'function_range',
                    'module': 'sympy.calculus.util',
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
                    'function': 'function_range',
                    'module': 'sympy.calculus.util'
                }
            }
