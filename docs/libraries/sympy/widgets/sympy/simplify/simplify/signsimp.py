"""
SymPy signsimp Widget
Make all Add sub-expressions canonical wrt sign. Explanation If an Add subexpression, ``a``, can have a sign extracted, as determined by could_extract_minus_sign, it is replaced with Mul(-1, a, evaluate=False). This allows signs to be extracted from powers and products. Examples >>> from sympy import signsimp, exp, symbols >>> from sympy.abc import x, y >>> i = symbols('i', odd=True) >>> n = -1 + 1/x >>> n/x/(-n)**2 - 1/n/x (-1 + 1/x)/(x*(1 - 1/x)**2) - 1/(x*(-1 + 1/x)) >>> signsimp(_) 0 >>> x*n + x*-n x*(-1 + 1/x) + x*(1 - 1/x) >>> signsimp(_) 0 Since powers automatically handle leading signs >>> (-2)**i -2**i signsimp can be used to put the base of a power with an integer exponent into canonical form: >>> n**i (-1 + 1/x)**i By default, signsimp does not leave behind any hollow simplification: if making an Add canonical wrt sign didn't change the expression, the original Add is restored. If this is not desired then the keyword ``evaluate`` can be set to False: >>> e = exp(y - x) >>> signsimp(e) == e True >>> signsimp(e, evaluate=False) exp(-(x - y))
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


class SymPySignsimpWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
