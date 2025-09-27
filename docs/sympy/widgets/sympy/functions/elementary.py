"""
SymPy Functions Elementary Widget
Widget for SymPy elementary functions
"""

from typing import Dict, Any
import sympy as sp


class SymPyFunctionsElementaryWidget:
    """Widget for SymPy elementary functions."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute elementary function operations."""
        try:
            # Parse expression
            expression_str = validated_input.get('expression', 'sin(x)')
            variables = validated_input.get('variables', ['x'])
            
            # Create SymPy symbols
            symbols = {var: sp.Symbol(var) for var in variables}
            
            # Parse expression
            expr = sp.sympify(expression_str, locals=symbols)
            
            # Apply various elementary function operations
            operations = {
                'original': expr,
                'simplified': sp.simplify(expr),
                'expanded': sp.expand(expr),
                'derivative': sp.diff(expr, symbols.get('x', sp.Symbol('x'))),
                'integral': sp.integrate(expr, symbols.get('x', sp.Symbol('x')))
            }
            
            result_parts = []
            for op_name, op_result in operations.items():
                result_parts.append(f"{op_name}: {op_result}")
            
            result = "\n".join(result_parts)
            latex = sp.latex(operations['simplified'])
            
            return {
                'result': result,
                'latex': latex,
                'metadata': {
                    'original_expression': str(expr),
                    'function_type': type(expr).__name__,
                    'symbols_used': [str(s) for s in expr.free_symbols],
                    'operations_applied': list(operations.keys())
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