"""
SymPy inversecombine Widget
Simplify the composition of a function and its inverse. Explanation No attention is paid to whether the inverse is a left inverse or a right inverse; thus, the result will in general not be equivalent to the original expression. Examples >>> from sympy.simplify.simplify import inversecombine >>> from sympy import asin, sin, log, exp >>> from sympy.abc import x >>> inversecombine(asin(sin(x))) x >>> inversecombine(2*log(exp(3*x))) 6*x
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import inversecombine


class SymPyInversecombineWidget(BaseSymPyWidget):
    """Widget for SymPy inversecombine function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return inversecombine
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'inversecombine',
            'module': 'sympy.simplify.simplify'
        }
