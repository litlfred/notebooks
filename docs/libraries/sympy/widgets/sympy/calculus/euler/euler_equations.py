"""
SymPy euler_equations Widget
Find the Euler-Lagrange equations [1]_ for a given Lagrangian.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.euler import euler_equations


class SymPyEuler_EquationsWidget(BaseSymPyWidget):
    """Widget for SymPy euler_equations function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return euler_equations
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'euler_equations',
            'module': 'sympy.calculus.euler'
        }
