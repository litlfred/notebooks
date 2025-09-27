"""
SymPy check_arguments Widget
Checks the arguments and converts into tuples of the form (exprs, ranges). Examples .. plot:: :context: reset :format: doctest :include-source: True >>> from sympy import cos, sin, symbols >>> from sympy.plotting.plot import check_arguments >>> x = symbols('x') >>> check_arguments([cos(x), sin(x)], 2, 1) [(cos(x), sin(x), (x, -10, 10))] >>> check_arguments([x, x**2], 1, 1) [(x, (x, -10, 10)), (x**2, (x, -10, 10))]
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import check_arguments


class SymPyCheck_ArgumentsWidget(BaseSymPyWidget):
    """Widget for SymPy check_arguments function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return check_arguments
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'check_arguments',
            'module': 'sympy.plotting.plot'
        }
