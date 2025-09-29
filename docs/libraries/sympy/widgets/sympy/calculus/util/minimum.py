"""
SymPy minimum Widget
Returns the minimum value of a function in the given domain.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import minimum


class SymPyWidgetsSympyCalculusUtilMinimumWidget(BaseSymPyWidget):
    """Widget for SymPy minimum function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return minimum
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'minimum',
            'module': 'sympy.calculus.util'
        }
