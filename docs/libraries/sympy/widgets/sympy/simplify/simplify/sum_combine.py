"""
SymPy sum_combine Widget
Helper function for Sum simplification Attempts to simplify a list of sums, by combining limits / sum function's returns the simplified sum
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import sum_combine


class SymPySum_CombineWidget(BaseSymPyWidget):
    """Widget for SymPy sum_combine function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return sum_combine
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'sum_combine',
            'module': 'sympy.simplify.simplify'
        }
