"""
SymPy a2idx Widget
Return integer after making positive and validating against n.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.matrices.common import a2idx


class SymPyA2IdxWidget(BaseSymPyWidget):
    """Widget for SymPy a2idx function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return a2idx
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'a2idx',
            'module': 'sympy.matrices.common'
        }
