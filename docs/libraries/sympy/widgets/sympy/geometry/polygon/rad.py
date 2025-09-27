"""
SymPy rad Widget
Return the radian value for the given degrees (pi = 180 degrees).
"""

from typing import Dict, Any
import sympy as sp
from sympy.geometry.polygon import rad


class SymPyRadWidget:
    """Widget for SymPy rad function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the rad function."""
        try:
            # Extract parameters from input
            d = validated_input.get('d', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['d'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = rad(d)
            
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
                    'function': 'rad',
                    'module': 'sympy.geometry.polygon',
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
                    'function': 'rad',
                    'module': 'sympy.geometry.polygon'
                }
            }
