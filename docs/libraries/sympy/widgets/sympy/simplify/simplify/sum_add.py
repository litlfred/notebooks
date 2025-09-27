"""
SymPy sum_add Widget
Helper function for Sum simplification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import sum_add


class SymPySum_AddWidget(BaseSymPyWidget):
    """Widget for SymPy sum_add function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sum_add
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sum_add',
            'module': 'sympy.simplify.simplify'
        }
