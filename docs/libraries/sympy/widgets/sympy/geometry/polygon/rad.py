"""
SymPy rad Widget
Return the radian value for the given degrees (pi = 180 degrees).
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.geometry.polygon import rad


class SymPyRadWidget(BaseSymPyWidget):
    """Widget for SymPy rad function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return rad
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'rad',
            'module': 'sympy.geometry.polygon'
        }
