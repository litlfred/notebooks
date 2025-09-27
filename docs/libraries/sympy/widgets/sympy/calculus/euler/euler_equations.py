"""
SymPy euler_equations Widget
Find the Euler-Lagrange equations [1]_ for a given Lagrangian.
"""

from typing import Dict, Any
import sympy as sp
from sympy.calculus.euler import euler_equations


class SymPyEuler_EquationsWidget:
    """Widget for SymPy euler_equations function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the euler_equations function."""
        try:
            # Extract parameters from input
            L = validated_input.get('L', None)
            funcs = validated_input.get('funcs', [])
            vars = validated_input.get('vars', '()')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['L', 'funcs', 'vars'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = euler_equations(L, funcs, vars)
            
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
                    'function': 'euler_equations',
                    'module': 'sympy.calculus.euler',
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
                    'function': 'euler_equations',
                    'module': 'sympy.calculus.euler'
                }
            }
