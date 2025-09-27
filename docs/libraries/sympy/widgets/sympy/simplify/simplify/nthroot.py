"""
SymPy nthroot Widget
Compute a real nth-root of a sum of surds.
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import nthroot


class SymPyNthrootWidget(BaseSymPyWidget):
    """Widget for SymPy nthroot function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return nthroot
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'nthroot',
            'module': 'sympy.simplify.simplify'
        }
