"""
SymPy minimum Widget
Returns the minimum value of a function in the given domain.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import minimum


class SymPyMinimumWidget(BaseSymPyWidget):
    """Widget for SymPy minimum function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return minimum
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'minimum',
            'module': 'sympy.calculus.util'
        }
