"""
SymPy expand_power_exp Widget
Wrapper around expand that only uses the power_exp hint. See the expand docstring for more information. Examples >>> from sympy import expand_power_exp, Symbol >>> from sympy.abc import x, y >>> expand_power_exp(3**(y + 2)) 9*3**y >>> expand_power_exp(x**(y + 2)) x**(y + 2) If ``x = 0`` the value of the expression depends on the value of ``y``; if the expression were expanded the result would be 0. So expansion is only done if ``x != 0``: >>> expand_power_exp(Symbol('x', zero=False)**(y + 2)) x**2*x**y
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import x


class SymPyWidgetsSympyCoreFunctionExpandpowerexpWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
