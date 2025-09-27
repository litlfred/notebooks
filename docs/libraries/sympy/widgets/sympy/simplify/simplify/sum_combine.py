"""
SymPy sum_combine Widget
Helper function for Sum simplification Attempts to simplify a list of sums, by combining limits / sum function's returns the simplified sum
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import sum_combine


class SymPySum_CombineWidget:
    """Widget for SymPy sum_combine function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the sum_combine function."""
        try:
            # Extract parameters from input
            s_t = validated_input.get('s_t', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['s_t'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = sum_combine(s_t)
            
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
                    'function': 'sum_combine',
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
                    'function': 'sum_combine',
                    'module': 'sympy.simplify.simplify'
                }
            }
