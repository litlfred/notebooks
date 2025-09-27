"""
SymPy maximum Widget
Returns the maximum value of a function in the given domain.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import maximum


class SymPyMaximumWidget(BaseSymPyWidget):
    """Widget for SymPy maximum function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return maximum
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'maximum',
            'module': 'sympy.calculus.util'
        }
