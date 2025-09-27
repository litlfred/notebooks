"""
SymPy count_ops Widget
Return a representation (integer or expression) of the operations in expr.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import count_ops


class SymPyCount_OpsWidget(BaseSymPyWidget):
    """Widget for SymPy count_ops function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return count_ops
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'count_ops',
            'module': 'sympy.core.function'
        }
