"""
SymPy lcim Widget
Returns the least common integral multiple of a list of numbers. The numbers can be rational or irrational or a mixture of both. `None` is returned for incommensurable numbers.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.util import lcim


class SymPyLcimWidget:
    """Widget for SymPy lcim function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the lcim function."""
        try:
            # Extract parameters from input
            numbers = validated_input.get('numbers', [])
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['numbers'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = lcim(numbers)
            
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
                    'function': 'lcim',
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
                    'function': 'lcim',
                    'module': 'sympy.calculus.util'
                }
            }
