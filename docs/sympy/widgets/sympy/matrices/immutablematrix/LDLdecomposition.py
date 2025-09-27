"""
Widget for SymPy ImmutableMatrix.LDLdecomposition method
"""

from typing import Dict, Any
import sympy as sp


class SymPyImmutableMatrixLdldecompositionWidget:
    """Widget for SymPy ImmutableMatrix.LDLdecomposition operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the ImmutableMatrix.LDLdecomposition operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "LDLdecomposition" and hasattr(expr, "LDLdecomposition"):
                # Method widget - call method on expression
                method = getattr(expr, "LDLdecomposition")
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
                    'widget_id': 'sympy-matrices-immutablematrix-LDLdecomposition',
                    'class_name': 'ImmutableMatrix',
                    'method_name': 'LDLdecomposition',
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
                    'widget_id': 'sympy-matrices-immutablematrix-LDLdecomposition',
                    'error_type': type(e).__name__
                }
            }
