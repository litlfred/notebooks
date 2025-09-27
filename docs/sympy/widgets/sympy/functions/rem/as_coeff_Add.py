"""
Widget for SymPy Rem.as_coeff_Add method
"""

from typing import Dict, Any
import sympy as sp


class SymPyRemAscoeffaddWidget:
    """Widget for SymPy Rem.as_coeff_Add operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Rem.as_coeff_Add operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "as_coeff_Add" and hasattr(expr, "as_coeff_Add"):
                # Method widget - call method on expression
                method = getattr(expr, "as_coeff_Add")
                result = method()
            else:
                # Class widget or generic operation
                result = expr
            
            # Format output
            result_str = str(result)
            latex_str = sp.latex(result)
            
            return {
                'result': result_str,
                'latex': latex_str,
                'metadata': {
                    'widget_id': 'sympy-functions-rem-as_coeff_Add',
                    'class_name': 'Rem',
                    'method_name': 'as_coeff_Add',
                    'module_name': 'sympy.functions',
                    'result_type': type(result).__name__
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'widget_id': 'sympy-functions-rem-as_coeff_Add',
                    'error_type': type(e).__name__
                }
            }
