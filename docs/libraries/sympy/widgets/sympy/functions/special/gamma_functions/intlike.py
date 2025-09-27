"""
SymPy intlike Widget
SymPy intlike function
"""

from typing import Dict, Any
import sympy as sp
from sympy.functions.special.gamma_functions import intlike


class SymPyIntlikeWidget:
    """Widget for SymPy intlike function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the intlike function."""
        try:
            # Extract parameters from input
            n = validated_input.get('n', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['n'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = intlike(n)
            
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
                    'function': 'intlike',
                    'module': 'sympy.functions.special.gamma_functions',
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
                    'function': 'intlike',
                    'module': 'sympy.functions.special.gamma_functions'
                }
            }
