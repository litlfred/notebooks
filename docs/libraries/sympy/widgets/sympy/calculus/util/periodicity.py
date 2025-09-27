"""
SymPy periodicity Widget
Tests the given function for periodicity in the given symbol.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import periodicity


class SymPyPeriodicityWidget(BaseSymPyWidget):
    """Widget for SymPy periodicity function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return periodicity
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'periodicity',
            'module': 'sympy.calculus.util'
        }
