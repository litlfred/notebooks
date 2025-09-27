"""
SymPy Core Add Widget
Widget for SymPy Add operations
"""

from typing import Dict, Any
import sympy as sp


class SymPyCoreAddWidget:
    """Widget for SymPy Add class operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Add operation."""
        try:
            # Parse expression
            expression_str = validated_input.get('expression', 'x + 1')
            variables = validated_input.get('variables', ['x'])
            
            # Create SymPy symbols
            symbols = {var: sp.Symbol(var) for var in variables}
            
            # Parse and evaluate expression
            expr = sp.sympify(expression_str, locals=symbols)
            
            # Perform Add operation if not already an Add
            if not isinstance(expr, sp.Add):
                # Create an Add expression by adding zero
                expr = sp.Add(expr, 0)
            
            # Generate outputs
            result = str(expr)
            latex = sp.latex(expr)
            
            return {
                'result': result,
                'latex': latex,
                'metadata': {
                    'expression_type': type(expr).__name__,
                    'symbols_used': list(expr.free_symbols),
                    'is_add': isinstance(expr, sp.Add),
                    'args': [str(arg) for arg in expr.args] if hasattr(expr, 'args') else []
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            }