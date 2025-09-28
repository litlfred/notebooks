"""
SymPy nfloat Widget
Make all Rationals in expr Floats except those in exponents (unless the exponents flag is set to True) and those in undefined functions. When processing dictionaries, do not modify the keys unless ``dkeys=True``. Examples >>> from sympy import nfloat, cos, pi, sqrt >>> from sympy.abc import x, y >>> nfloat(x**4 + x/2 + cos(pi/3) + 1 + sqrt(y)) x**4 + 0.5*x + sqrt(y) + 1.5 >>> nfloat(x**4 + sqrt(y), exponent=True) x**4.0 + y**0.5 Container types are not modified: >>> type(nfloat((1, 2))) is tuple True
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


class SymPyWidgetsSympyCoreFunctionNfloatWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
