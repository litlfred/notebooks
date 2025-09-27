"""
SymPy arity Widget
Return the arity of the function if it is known, else None. Explanation When default values are specified for some arguments, they are optional and the arity is reported as a tuple of possible values. Examples >>> from sympy import arity, log >>> arity(lambda x: x) 1 >>> arity(log) (1, 2) >>> arity(lambda *x: sum(x)) is None True
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import arity


class SymPyArityWidget(BaseSymPyWidget):
    """Widget for SymPy arity function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return arity
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'arity',
            'module': 'sympy.core.function'
        }
