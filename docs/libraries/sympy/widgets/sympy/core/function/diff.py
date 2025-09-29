"""
SymPy diff Widget
Differentiate f with respect to symbols.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import diff


class SymPyWidgetsSympyCoreFunctionDiffWidget(BaseSymPyWidget):
    """Widget for SymPy diff function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return diff
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'diff',
            'module': 'sympy.core.function'
        }
