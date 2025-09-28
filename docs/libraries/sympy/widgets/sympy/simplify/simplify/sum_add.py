"""
SymPy sum_add Widget
Helper function for Sum simplification
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import sum_add


class SymPyWidgetsSympySimplifySimplifySumaddWidget(BaseSymPyWidget):
    """Widget for SymPy sum_add function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sum_add
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sum_add',
            'module': 'sympy.simplify.simplify'
        }
