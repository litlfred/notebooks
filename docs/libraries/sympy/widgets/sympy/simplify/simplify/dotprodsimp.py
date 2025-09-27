"""
SymPy dotprodsimp Widget
Simplification for a sum of products targeted at the kind of blowup that occurs during summation of products. Intended to reduce expression blowup during matrix multiplication or other similar operations. Only works with algebraic expressions and does not recurse into non.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import dotprodsimp


class SymPyDotprodsimpWidget(BaseSymPyWidget):
    """Widget for SymPy dotprodsimp function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return dotprodsimp
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'dotprodsimp',
            'module': 'sympy.simplify.simplify'
        }
