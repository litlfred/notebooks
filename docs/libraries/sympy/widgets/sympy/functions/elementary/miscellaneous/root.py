"""
SymPy root Widget
Returns the *k*-th *n*-th root of ``arg``.
"""

from typing import Dict, Any
import sympy as sp
from sympy.functions.elementary.miscellaneous import root


class SymPyRootWidget:
    """Widget for SymPy root function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the root function."""
        try:
            # Extract parameters from input
            arg = validated_input.get('arg', None)
            n = validated_input.get('n', None)
            k = validated_input.get('k', '0')
            evaluate = validated_input.get('evaluate', False)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['arg', 'n', 'k', 'evaluate'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = root(arg, n, k, evaluate)
            
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
                    'function': 'root',
                    'module': 'sympy.functions.elementary.miscellaneous',
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
                    'function': 'root',
                    'module': 'sympy.functions.elementary.miscellaneous'
                }
            }
