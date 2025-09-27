"""
Widget for SymPy Ge.as_set method
"""

from typing import Dict, Any
import sympy as sp


class SymPyGeAssetWidget:
    """Widget for SymPy Ge.as_set operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Ge.as_set operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "as_set" and hasattr(expr, "as_set"):
                # Method widget - call method on expression
                method = getattr(expr, "as_set")
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
                    'widget_id': 'sympy-core-ge-as_set',
                    'class_name': 'Ge',
                    'method_name': 'as_set',
                    'module_name': 'sympy.core',
                    'result_type': type(result).__name__
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'widget_id': 'sympy-core-ge-as_set',
                    'error_type': type(e).__name__
                }
            }
