"""
SymPy stationary_points Widget
Returns the stationary points of a function (where derivative of the function is 0) in the given domain.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import stationary_points


class SymPyWidgetsSympyCalculusUtilStationarypointsWidget(BaseSymPyWidget):
    """Widget for SymPy stationary_points function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return stationary_points
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'stationary_points',
            'module': 'sympy.calculus.util'
        }
