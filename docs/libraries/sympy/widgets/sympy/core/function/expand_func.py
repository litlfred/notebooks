"""
SymPy expand_func Widget
Wrapper around expand that only uses the func hint.  See the expand docstring for more information. Examples >>> from sympy import expand_func, gamma >>> from sympy.abc import x >>> expand_func(gamma(x + 2)) x*(x + 1)*gamma(x)
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


class SymPyExpand_FuncWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
