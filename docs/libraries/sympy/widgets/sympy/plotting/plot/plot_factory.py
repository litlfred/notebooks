"""
SymPy plot_factory Widget
SymPy plot_factory function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import plot_factory


class SymPyPlot_FactoryWidget(BaseSymPyWidget):
    """Widget for SymPy plot_factory function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return plot_factory
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'plot_factory',
            'module': 'sympy.plotting.plot'
        }
