"""
SymPy expand_mul Widget
Wrapper around expand that only uses the mul hint.  See the expand docstring for more information. Examples >>> from sympy import symbols, expand_mul, exp, log >>> x, y = symbols('x,y', positive=True) >>> expand_mul(exp(x+y)*(x+y)*log(x*y**2)) x*exp(x + y)*log(x*y**2) + y*exp(x + y)*log(x*y**2)
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import expand_mul


class SymPyExpand_MulWidget(BaseSymPyWidget):
    """Widget for SymPy expand_mul function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return expand_mul
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'expand_mul',
            'module': 'sympy.core.function'
        }
