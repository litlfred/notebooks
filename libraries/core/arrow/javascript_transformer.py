"""
JavaScript Transformer Implementation
Provides JavaScript/Node.js transformation support via Node.js modules
"""

from typing import List
from .transformers import NodeJSTransformer, TransformerFactory


class JavaScriptTransformer(NodeJSTransformer):
    """JavaScript/Node.js transformation support"""
    
    def __init__(self):
        super().__init__('notebooks-transformers-js', 'javascript')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/javascript', 'text/javascript']


# Register JavaScript transformer
TransformerFactory.register_transformer(JavaScriptTransformer())