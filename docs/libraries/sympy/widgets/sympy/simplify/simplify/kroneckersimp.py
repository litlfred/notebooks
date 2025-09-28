"""
SymPy kroneckersimp Widget
Simplify expressions with KroneckerDelta. The only simplification currently attempted is to identify multiplicative cancellation: Examples >>> from sympy import KroneckerDelta, kroneckersimp >>> from sympy.abc import i >>> kroneckersimp(1 + KroneckerDelta(0, i) * KroneckerDelta(1, i)) 1
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import i


class SymPyWidgetsSympySimplifySimplifyKroneckersimpWidget(BaseSymPyWidget):
    """Widget for SymPy i function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return i
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'i',
            'module': 'sympy.abc'
        }
