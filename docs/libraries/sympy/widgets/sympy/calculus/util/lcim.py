"""
SymPy lcim Widget
Returns the least common integral multiple of a list of numbers. The numbers can be rational or irrational or a mixture of both. `None` is returned for incommensurable numbers.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import lcim


class SymPyWidgetsSympyCalculusUtilLcimWidget(BaseSymPyWidget):
    """Widget for SymPy lcim function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return lcim
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'lcim',
            'module': 'sympy.calculus.util'
        }
