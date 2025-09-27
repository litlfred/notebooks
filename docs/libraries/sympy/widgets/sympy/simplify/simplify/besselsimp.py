"""
from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import besselsimp


class SymPyBesselsimpWidget:
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import z


class SymPyBesselsimpWidget(BaseSymPyWidget):
    """Widget for SymPy z function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return z
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'z',
            'module': 'sympy.abc'
        }
