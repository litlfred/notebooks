"""
SymPy expand_complex Widget
Wrapper around expand that only uses the complex hint.  See the expand docstring for more information. Examples >>> from sympy import expand_complex, exp, sqrt, I >>> from sympy.abc import z >>> expand_complex(exp(z)) I*exp(re(z))*sin(im(z)) + exp(re(z))*cos(im(z)) >>> expand_complex(sqrt(I)) sqrt(2)/2 + sqrt(2)*I/2 See Also sympy.core.expr.Expr.as_real_imag
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import z


class SymPyWidgetsSympyCoreFunctionExpandcomplexWidget(BaseSymPyWidget):
    """Widget for SymPy z function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return z
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'z',
            'module': 'sympy.abc'
        }
