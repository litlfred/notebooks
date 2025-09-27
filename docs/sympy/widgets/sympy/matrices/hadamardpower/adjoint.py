"""
Widget for SymPy HadamardPower.adjoint method
"""

from typing import Dict, Any
import sympy as sp


class SymPyHadamardPowerAdjointWidget:
    """Widget for SymPy HadamardPower.adjoint operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the HadamardPower.adjoint operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "adjoint" and hasattr(expr, "adjoint"):
                # Method widget - call method on expression
                method = getattr(expr, "adjoint")
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
                    'widget_id': 'sympy-matrices-hadamardpower-adjoint',
                    'class_name': 'HadamardPower',
                    'method_name': 'adjoint',
                    'module_name': 'sympy.matrices',
                    'result_type': type(result).__name__
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'widget_id': 'sympy-matrices-hadamardpower-adjoint',
                    'error_type': type(e).__name__
                }
            }
