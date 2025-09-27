"""
SymPy factor_sum Widget
Return Sum with constant factors extracted. If ``limits`` is specified then ``self`` is the summand; the other keywords are passed to ``factor_terms``. Examples >>> from sympy import Sum >>> from sympy.abc import x, y >>> from sympy.simplify.simplify import factor_sum >>> s = Sum(x*y, (x, 1, 3)) >>> factor_sum(s) y*Sum(x, (x, 1, 3)) >>> factor_sum(s.function, s.limits) y*Sum(x, (x, 1, 3))
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


class SymPyFactor_SumWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
