"""
SymPy expand_trig Widget
Wrapper around expand that only uses the trig hint.  See the expand docstring for more information. Examples >>> from sympy import expand_trig, sin >>> from sympy.abc import x, y >>> expand_trig(sin(x+y)*(x+y)) (x + y)*(sin(x)*cos(y) + sin(y)*cos(x))
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


class SymPyWidgetsSympyCoreFunctionExpandtrigWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
