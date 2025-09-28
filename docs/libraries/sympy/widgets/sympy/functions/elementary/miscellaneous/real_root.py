"""
SymPy real_root Widget
Return the real *n*'th-root of *arg* if possible.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import real_root


class SymPyWidgetsSympyFunctionsElementaryMiscellaneousRealrootWidget(BaseSymPyWidget):
    """Widget for SymPy real_root function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return real_root
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'real_root',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
