"""
Widget for SymPy ImmutableDenseMatrix.LUdecomposition method
"""

from typing import Dict, Any
import sympy as sp


class SymPyImmutableDenseMatrixLudecompositionWidget:
    """Widget for SymPy ImmutableDenseMatrix.LUdecomposition operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the ImmutableDenseMatrix.LUdecomposition operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "LUdecomposition" and hasattr(expr, "LUdecomposition"):
                # Method widget - call method on expression
                method = getattr(expr, "LUdecomposition")
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
                    'widget_id': 'sympy-matrices-immutabledensematrix-LUdecomposition',
                    'class_name': 'ImmutableDenseMatrix',
                    'method_name': 'LUdecomposition',
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
                    'widget_id': 'sympy-matrices-immutabledensematrix-LUdecomposition',
                    'error_type': type(e).__name__
                }
            }
