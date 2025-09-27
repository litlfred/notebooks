"""
SymPy kroneckersimp Widget
Simplify expressions with KroneckerDelta. The only simplification currently attempted is to identify multiplicative cancellation: Examples >>> from sympy import KroneckerDelta, kroneckersimp >>> from sympy.abc import i >>> kroneckersimp(1 + KroneckerDelta(0, i) * KroneckerDelta(1, i)) 1
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import kroneckersimp


class SymPyKroneckersimpWidget:
    """Widget for SymPy kroneckersimp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the kroneckersimp function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = kroneckersimp(expr)
            
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
                    'function': 'kroneckersimp',
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
                    'function': 'kroneckersimp',
                    'module': 'sympy.simplify.simplify'
                }
            }
