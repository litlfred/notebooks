"""
SymPy sqrt Widget
Returns the principal square root.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import sqrt


class SymPySqrtWidget(BaseSymPyWidget):
    """Widget for SymPy sqrt function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sqrt
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sqrt',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
