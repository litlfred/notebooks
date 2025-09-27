"""
SymPy check_arguments Widget
Checks the arguments and converts into tuples of the form (exprs, ranges). Examples .. plot:: :context: reset :format: doctest :include-source: True >>> from sympy import cos, sin, symbols >>> from sympy.plotting.plot import check_arguments >>> x = symbols('x') >>> check_arguments([cos(x), sin(x)], 2, 1) [(cos(x), sin(x), (x, -10, 10))] >>> check_arguments([x, x**2], 1, 1) [(x, (x, -10, 10)), (x**2, (x, -10, 10))]
"""

from typing import Dict, Any
import sympy as sp
from sympy.plotting.plot import check_arguments


class SymPyCheck_ArgumentsWidget:
    """Widget for SymPy check_arguments function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the check_arguments function."""
        try:
            # Extract parameters from input
            args = validated_input.get('args', None)
            expr_len = validated_input.get('expr_len', None)
            nb_of_free_symbols = validated_input.get('nb_of_free_symbols', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['args', 'expr_len', 'nb_of_free_symbols'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = check_arguments(args, expr_len, nb_of_free_symbols)
            
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
                    'function': 'check_arguments',
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
                    'function': 'check_arguments',
                    'module': 'sympy.plotting.plot'
                }
            }
