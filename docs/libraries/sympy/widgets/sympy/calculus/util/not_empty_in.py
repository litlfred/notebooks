"""
SymPy not_empty_in Widget
Finds the domain of the functions in ``finset_intersection`` in which the ``finite_set`` is not-empty.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.util import not_empty_in


class SymPyNot_Empty_InWidget:
    """Widget for SymPy not_empty_in function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the not_empty_in function."""
        try:
            # Extract parameters from input
            finset_intersection = validated_input.get('finset_intersection', None)
            syms = validated_input.get('syms', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['finset_intersection', 'syms'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = not_empty_in(finset_intersection, syms)
            
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
                    'function': 'not_empty_in',
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
                    'function': 'not_empty_in',
                    'module': 'sympy.calculus.util'
                }
            }
