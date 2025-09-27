"""
SymPy a2idx Widget
Return integer after making positive and validating against n.
"""

from typing import Dict, Any
import sympy as sp
from sympy.matrices.common import a2idx


class SymPyA2IdxWidget:
    """Widget for SymPy a2idx function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the a2idx function."""
        try:
            # Extract parameters from input
            j = validated_input.get('j', None)
            n = validated_input.get('n', 'None')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['j', 'n'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = a2idx(j, n)
            
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
                    'function': 'a2idx',
                    'module': 'sympy.matrices.common',
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
                    'function': 'a2idx',
                    'module': 'sympy.matrices.common'
                }
            }
