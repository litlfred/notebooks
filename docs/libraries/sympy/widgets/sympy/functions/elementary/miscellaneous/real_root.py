"""
SymPy real_root Widget
Return the real *n*'th-root of *arg* if possible.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.functions.elementary.miscellaneous import real_root


class SymPyReal_RootWidget(BaseSymPyWidget):
    """Widget for SymPy real_root function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return real_root
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'real_root',
            'module': 'sympy.functions.elementary.miscellaneous'
        }
