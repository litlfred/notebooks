"""
from typing import Dict, Any
import sympy as sp
from sympy.functions.special.bessel import jn_zeros


class SymPyJn_ZerosWidget:
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.special.bessel import jn_zeros


class SymPyJn_ZerosWidget(BaseSymPyWidget):
    """Widget for SymPy jn_zeros function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return jn_zeros
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'jn_zeros',
            'module': 'sympy.functions.special.bessel'
        }
