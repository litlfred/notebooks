"""
SymPy expand_power_exp Widget
Wrapper around expand that only uses the power_exp hint. See the expand docstring for more information. Examples >>> from sympy import expand_power_exp, Symbol >>> from sympy.abc import x, y >>> expand_power_exp(3**(y + 2)) 9*3**y >>> expand_power_exp(x**(y + 2)) x**(y + 2) If ``x = 0`` the value of the expression depends on the value of ``y``; if the expression were expanded the result would be 0. So expansion is only done if ``x != 0``: >>> expand_power_exp(Symbol('x', zero=False)**(y + 2)) x**2*x**y
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import expand_power_exp


class SymPyExpand_Power_ExpWidget:
    """Widget for SymPy expand_power_exp function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the expand_power_exp function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            deep = validated_input.get('deep', 'True')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'deep'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = expand_power_exp(expr, deep)
            
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
                    'function': 'expand_power_exp',
                    'module': 'sympy.core.function',
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
                    'function': 'expand_power_exp',
                    'module': 'sympy.core.function'
                }
            }
