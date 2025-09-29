"""
Arrow package initialization
Imports transformers and sets up the transformation system
"""

from .arrow import WorkflowArrow
from .transformers import BaseTransformer, TransformerFactory, PythonTransformer, NodeJSTransformer

# Import and register available transformers
try:
    from .javascript_transformer import JavaScriptTransformer
except ImportError:
    # JavaScript transformer not available
    pass

__all__ = [
    'WorkflowArrow',
    'BaseTransformer', 
    'TransformerFactory',
    'PythonTransformer',
    'NodeJSTransformer'
]