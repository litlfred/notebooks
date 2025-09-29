"""
SymPy product_mul Widget
Helper function for Product simplification
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import product_mul


class SymPyWidgetsSympySimplifySimplifyProductmulWidget(BaseSymPyWidget):
    """Widget for SymPy product_mul function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return product_mul
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'product_mul',
            'module': 'sympy.simplify.simplify'
        }
