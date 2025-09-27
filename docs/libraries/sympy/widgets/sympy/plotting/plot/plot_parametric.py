"""
SymPy plot_parametric Widget
Plots a 2D parametric curve.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import plot_parametric


class SymPyPlot_ParametricWidget(BaseSymPyWidget):
    """Widget for SymPy plot_parametric function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return plot_parametric
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'plot_parametric',
            'module': 'sympy.plotting.plot'
        }
