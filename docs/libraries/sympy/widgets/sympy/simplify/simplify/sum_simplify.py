"""
SymPy sum_simplify Widget
Main function for Sum simplification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import sum_simplify


class SymPySum_SimplifyWidget(BaseSymPyWidget):
    """Widget for SymPy sum_simplify function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sum_simplify
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sum_simplify',
            'module': 'sympy.simplify.simplify'
        }
