"""
SymPy match_real_imag Widget
Try to match expr with $a + Ib$ for real $a$ and $b$. ``match_real_imag`` returns a tuple containing the real and imaginary parts of expr or ``(None, None)`` if direct matching is not possible. Contrary to :func:`~.re`, :func:`~.im``, and ``as_real_imag()``, this helper will not force things by returning expressions themselves containing ``re()`` or ``im()`` and it does not expand its argument either.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.exponential import match_real_imag


class SymPyMatch_Real_ImagWidget(BaseSymPyWidget):
    """Widget for SymPy match_real_imag function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return match_real_imag
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'match_real_imag',
            'module': 'sympy.functions.elementary.exponential'
        }
