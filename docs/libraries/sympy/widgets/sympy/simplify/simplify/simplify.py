"""
SymPy simplify Widget
Simplifies the given expression with intelligent heuristics.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import simplify


class SymPySimplifyWidget(BaseSymPyWidget):
    """Widget for SymPy simplify function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return simplify
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'simplify',
            'module': 'sympy.simplify.simplify'
        }
