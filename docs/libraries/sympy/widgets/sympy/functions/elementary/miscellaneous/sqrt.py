"""
SymPy sqrt Widget
Returns the principal square root.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import sqrt


class SymPyWidgetsSympyFunctionsElementaryMiscellaneousSqrtWidget(BaseSymPyWidget):
    """Widget for SymPy sqrt function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sqrt
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sqrt',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
