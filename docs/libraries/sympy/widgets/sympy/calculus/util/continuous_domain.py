"""
SymPy continuous_domain Widget
Returns the domain on which the function expression f is continuous. This function is limited by the ability to determine the various singularities and discontinuities of the given function. The result is either given as a union of intervals or constructed using other set operations.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import continuous_domain


class SymPyContinuous_DomainWidget(BaseSymPyWidget):
    """Widget for SymPy continuous_domain function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return continuous_domain
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'continuous_domain',
            'module': 'sympy.calculus.util'
        }
