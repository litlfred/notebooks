"""
Widget for SymPy AtomicExpr.apart method
"""

from typing import Dict, Any
import sympy as sp


class SymPyAtomicExprApartWidget:
    """Widget for SymPy AtomicExpr.apart operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the AtomicExpr.apart operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "apart" and hasattr(expr, "apart"):
                # Method widget - call method on expression
                method = getattr(expr, "apart")
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
                    'widget_id': 'sympy-core-atomicexpr-apart',
                    'class_name': 'AtomicExpr',
                    'method_name': 'apart',
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
                    'widget_id': 'sympy-core-atomicexpr-apart',
                    'error_type': type(e).__name__
                }
            }
