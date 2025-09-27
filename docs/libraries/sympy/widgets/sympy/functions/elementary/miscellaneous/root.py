"""
SymPy root Widget
Returns the *k*-th *n*-th root of ``arg``.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import root


class SymPyRootWidget(BaseSymPyWidget):
    """Widget for SymPy root function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return root
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'root',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
