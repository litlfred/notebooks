"""
SymPy intlike Widget
SymPy intlike function
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.functions.special.gamma_functions import intlike


class SymPyWidgetsSympyFunctionsSpecialGammafunctionsIntlikeWidget(BaseSymPyWidget):
    """Widget for SymPy intlike function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return intlike
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'intlike',
            'module': 'sympy.functions.special.gamma_functions'
        }
