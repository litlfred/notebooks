"""
SymPy periodicity Widget
Tests the given function for periodicity in the given symbol.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.util import periodicity


class SymPyPeriodicityWidget:
    """Widget for SymPy periodicity function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the periodicity function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            symbol = validated_input.get('symbol', None)
            check = validated_input.get('check', False)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'symbol', 'check'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = periodicity(f, symbol, check)
            
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
                    'function': 'periodicity',
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
                    'function': 'periodicity',
                    'module': 'sympy.calculus.util'
                }
            }
