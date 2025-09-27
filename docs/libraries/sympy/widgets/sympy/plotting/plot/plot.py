"""
SymPy plot Widget
Plots a function of a single variable as a curve.
"""

from typing import Dict, Any
import sympy as sp
from sympy.plotting.plot import plot


class SymPyPlotWidget:
    """Widget for SymPy plot function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot function."""
        try:
            # Extract parameters from input
            args = validated_input.get('args', None)
            show = validated_input.get('show', True)
            kwargs = validated_input.get('kwargs', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['args', 'show', 'kwargs'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = plot(args, show, kwargs)
            
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
                    'function': 'plot',
                    'module': 'sympy.plotting.plot',
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
                    'function': 'plot',
                    'module': 'sympy.plotting.plot'
                }
            }
