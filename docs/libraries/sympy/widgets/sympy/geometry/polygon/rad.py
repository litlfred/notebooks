"""
SymPy rad Widget
Return the radian value for the given degrees (pi = 180 degrees).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.geometry.polygon import rad


class SymPyRadWidget(BaseSymPyWidget):
    """Widget for SymPy rad function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return rad
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'rad',
            'module': 'sympy.geometry.polygon'
        }
