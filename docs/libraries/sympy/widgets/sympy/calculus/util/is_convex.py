"""
SymPy is_convex Widget
Determines the  convexity of the function passed in the argument.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import is_convex


class SymPyIs_ConvexWidget(BaseSymPyWidget):
    """Widget for SymPy is_convex function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return is_convex
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'is_convex',
            'module': 'sympy.calculus.util'
        }
