"""
Widget for SymPy Atom.atoms method
"""

from typing import Dict, Any
import sympy as sp


class SymPyAtomAtomsWidget:
    """Widget for SymPy Atom.atoms operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Atom.atoms operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "atoms" and hasattr(expr, "atoms"):
                # Method widget - call method on expression
                method = getattr(expr, "atoms")
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
                    'widget_id': 'sympy-core-atom-atoms',
                    'class_name': 'Atom',
                    'method_name': 'atoms',
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
                    'widget_id': 'sympy-core-atom-atoms',
                    'error_type': type(e).__name__
                }
            }
