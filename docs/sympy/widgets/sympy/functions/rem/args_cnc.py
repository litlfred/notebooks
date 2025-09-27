"""
Widget for SymPy Rem.args_cnc method
"""

from typing import Dict, Any
import sympy as sp


class SymPyRemArgscncWidget:
    """Widget for SymPy Rem.args_cnc operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Rem.args_cnc operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "args_cnc" and hasattr(expr, "args_cnc"):
                # Method widget - call method on expression
                method = getattr(expr, "args_cnc")
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
                    'widget_id': 'sympy-functions-rem-args_cnc',
                    'class_name': 'Rem',
                    'method_name': 'args_cnc',
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
                    'widget_id': 'sympy-functions-rem-args_cnc',
                    'error_type': type(e).__name__
                }
            }
