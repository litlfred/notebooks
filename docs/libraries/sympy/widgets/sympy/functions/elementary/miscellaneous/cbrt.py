"""
SymPy cbrt Widget
Returns the principal cube root.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import cbrt


class SymPyWidgetsSympyFunctionsElementaryMiscellaneousCbrtWidget(BaseSymPyWidget):
    """Widget for SymPy cbrt function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return cbrt
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'cbrt',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
