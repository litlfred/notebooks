"""
SymPy function_range Widget
Finds the range of a function in a given domain. This method is limited by the ability to determine the singularities and determine limits.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import function_range


class SymPyFunction_RangeWidget(BaseSymPyWidget):
    """Widget for SymPy function_range function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return function_range
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'function_range',
            'module': 'sympy.calculus.util'
        }
