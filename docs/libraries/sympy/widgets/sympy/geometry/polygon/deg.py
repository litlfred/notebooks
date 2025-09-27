"""
SymPy deg Widget
Return the degree value for the given radians (pi = 180 degrees).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.geometry.polygon import deg


class SymPyDegWidget(BaseSymPyWidget):
    """Widget for SymPy deg function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return deg
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'deg',
            'module': 'sympy.geometry.polygon'
        }
