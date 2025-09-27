"""
SymPy stationary_points Widget
Returns the stationary points of a function (where derivative of the function is 0) in the given domain.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.util import stationary_points


class SymPyStationary_PointsWidget:
    """Widget for SymPy stationary_points function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the stationary_points function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            symbol = validated_input.get('symbol', None)
            domain = validated_input.get('domain', 'Reals')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'symbol', 'domain'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = stationary_points(f, symbol, domain)
            
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
                    'function': 'stationary_points',
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
                    'function': 'stationary_points',
                    'module': 'sympy.calculus.util'
                }
            }
