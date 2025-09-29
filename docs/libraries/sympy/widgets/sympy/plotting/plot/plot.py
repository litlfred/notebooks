"""
SymPy plot Widget
Plots a function of a single variable as a curve.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import plot


class SymPyWidgetsSympyPlottingPlotPlotWidget(BaseSymPyWidget):
    """Widget for SymPy plot function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return plot
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'plot',
            'module': 'sympy.plotting.plot'
        }
