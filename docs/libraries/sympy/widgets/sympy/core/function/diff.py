"""
SymPy diff Widget
Differentiate f with respect to symbols.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import diff


class SymPyDiffWidget(BaseSymPyWidget):
    """Widget for SymPy diff function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return diff
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'diff',
            'module': 'sympy.core.function'
        }
