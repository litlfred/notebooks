"""
SymPy Widget Executor
Extends the existing widget executor system to handle SymPy widgets
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the existing widget executor
from ..weierstrass_playground.widgets.widget_executor import WidgetExecutor

# Import SymPy widget implementations
from .widgets.sympy_core_add import SymPyCoreAddWidget
from .widgets.sympy_functions_elementary import SymPyFunctionsElementaryWidget
from .widgets.sympy_matrices_dense import SymPyMatricesDenseWidget


class SymPyWidgetExecutor(WidgetExecutor):
    """Extended widget executor for SymPy widgets."""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SymPy widget based on widget type."""
        widget_id = self.schema.get('id', '')
        
        try:
            # Route to appropriate SymPy widget
            if widget_id == 'sympy-core-add':
                widget = SymPyCoreAddWidget(self.schema)
                return widget.execute(validated_input)
            elif widget_id.startswith('sympy-functions'):
                widget = SymPyFunctionsElementaryWidget(self.schema)
                return widget.execute(validated_input)
            elif widget_id.startswith('sympy-matrices'):
                widget = SymPyMatricesDenseWidget(self.schema)
                return widget.execute(validated_input)
            else:
                # Generic SymPy widget execution
                return self._execute_generic_sympy(validated_input, widget_id)
                
        except Exception as e:
            return {
                'result': f"Error executing SymPy widget: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'widget_id': widget_id
                }
            }
    
    def _execute_generic_sympy(self, validated_input: Dict[str, Any], widget_id: str) -> Dict[str, Any]:
        """Generic execution for SymPy widgets that don't have specific implementations."""
        import sympy as sp
        
        try:
            expression_str = validated_input.get('expression', 'x')
            variables = validated_input.get('variables', ['x'])
            
            # Create symbols
            symbols = {var: sp.Symbol(var) for var in variables}
            
            # Parse expression
            expr = sp.sympify(expression_str, locals=symbols)
            
            # Apply basic operations
            result = str(expr)
            latex = sp.latex(expr)
            
            return {
                'result': result,
                'latex': latex,
                'metadata': {
                    'widget_id': widget_id,
                    'expression_type': type(expr).__name__,
                    'symbols': [str(s) for s in expr.free_symbols]
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error in generic SymPy execution: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'widget_id': widget_id
                }
            }


def create_sympy_widget(widget_id: str, schemas: Dict[str, Any]) -> SymPyWidgetExecutor:
    """Factory function to create SymPy widgets."""
    if widget_id not in schemas.get('widget-schemas', {}):
        raise ValueError(f"Widget schema not found for: {widget_id}")
    
    schema = schemas['widget-schemas'][widget_id]
    return SymPyWidgetExecutor(schema)