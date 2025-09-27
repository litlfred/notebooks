"""
SymPy cbrt Widget
Returns the principal cube root.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import cbrt


class SymPyCbrtWidget(BaseSymPyWidget):
    """Widget for SymPy cbrt function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return cbrt
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'cbrt',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
