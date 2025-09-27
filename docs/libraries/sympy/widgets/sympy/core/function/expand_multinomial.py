"""
SymPy expand_multinomial Widget
Wrapper around expand that only uses the multinomial hint.  See the expand docstring for more information. Examples >>> from sympy import symbols, expand_multinomial, exp >>> x, y = symbols('x y', positive=True) >>> expand_multinomial((x + exp(x + 1))**2) x**2 + 2*x*exp(x + 1) + exp(2*x + 2)
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import expand_multinomial


class SymPyExpand_MultinomialWidget(BaseSymPyWidget):
    """Widget for SymPy expand_multinomial function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return expand_multinomial
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'expand_multinomial',
            'module': 'sympy.core.function'
        }
