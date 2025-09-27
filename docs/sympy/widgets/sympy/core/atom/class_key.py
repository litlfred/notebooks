"""
Widget for SymPy Atom.class_key method
"""

from typing import Dict, Any
import sympy as sp


class SymPyAtomClasskeyWidget:
    """Widget for SymPy Atom.class_key operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Atom.class_key operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "class_key" and hasattr(expr, "class_key"):
                # Method widget - call method on expression
                method = getattr(expr, "class_key")
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
                    'widget_id': 'sympy-core-atom-class_key',
                    'class_name': 'Atom',
                    'method_name': 'class_key',
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
                    'widget_id': 'sympy-core-atom-class_key',
                    'error_type': type(e).__name__
                }
            }
