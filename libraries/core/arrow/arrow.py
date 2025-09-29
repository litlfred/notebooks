"""
Workflow Arrow Implementation
Represents connections between widgets with optional ETL transformations
"""

import json
import inspect
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from .transformers import TransformerFactory


class WorkflowArrow:
    """
    Represents a connection arrow between widgets with optional transformation logic.
    Supports ETL (Extract, Transform, Load) pattern for parameter flow.
    Now supports multiple transformation languages via MIME types.
    """
    
    def __init__(self, arrow_config: Dict[str, Any]):
        self.source_widget = arrow_config['source_widget']
        self.target_widget = arrow_config['target_widget'] 
        self.source_parameters = arrow_config['source_parameters']
        self.target_parameters = arrow_config['target_parameters']
        self.arrow_type = arrow_config.get('arrow_type', 'parameter_flow')
        self.comment = arrow_config.get('comment', '')
        self.transformation = arrow_config.get('transformation', {})
        
        # Compile optional transformation function
        self.transform_function = None
        if self.transformation:
            self._compile_transformation()
    
    def _compile_transformation(self):
        """Compile transformation based on content type using appropriate transformer"""
        # Use multi-type system only - no legacy support
        content_type = self.transformation.get('content_type')
        if not content_type:
            raise ValueError("content_type is required in transformation")
        
        content = self._resolve_content()
        
        if not content.strip():
            return  # No transformation content
        
        try:
            # Get transformer implementation for content type
            transformer = TransformerFactory.get_transformer(content_type)
            
            # Validate content first
            if not transformer.validate_content(content, self.transformation):
                raise ValueError(f"Invalid {content_type} transformation content")
            
            # Compile transformation
            self.transform_function = transformer.compile(content, self.transformation)
            self.transformer = transformer
            
        except ValueError as e:
            raise ValueError(f"Failed to compile transformation: {e}")
    
    def _resolve_content(self) -> str:
        """Resolve content from inline, URL, or IRI source"""
        content_source = self.transformation.get('content_source', 'inline')
        
        if content_source == 'inline':
            return self.transformation.get('content', '')
        elif content_source in ['url', 'iri']:
            url = self.transformation.get('source_url')
            if url:
                return self._fetch_content(url)
            else:
                raise ValueError(f"Missing source_url for {content_source} content source")
        else:
            raise ValueError(f"Unsupported content source: {content_source}")
    
    def _fetch_content(self, url: str) -> str:
        """Fetch content from URL with proper caching and security"""
        # TODO: Implement URL fetching with security validation
        # For now, raise an error to indicate this feature needs implementation
        raise NotImplementedError("URL-based content fetching not yet implemented")
    
    def execute_connection(self, source_widget_instance, target_widget_instance) -> Dict[str, Any]:
        """Execute the arrow connection by transferring parameters from source to target."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Extract parameters from source widget
            source_data = {}
            for param in self.source_parameters:
                if hasattr(source_widget_instance, 'output_variables') and param in source_widget_instance.output_variables:
                    source_data[param] = source_widget_instance.output_variables[param]
                else:
                    source_data[param] = getattr(source_widget_instance, param, None)
            
            # Apply optional transformation
            transformed_data = source_data.copy()
            transformation_applied = False
            transformation_info = {}
            
            if self.transform_function and hasattr(self, 'transformer'):
                try:
                    input_mapping = self.transformation.get('input_mapping', {})
                    transformed_data = self.transformer.execute(
                        self.transform_function, 
                        source_data, 
                        input_mapping
                    )
                    transformation_applied = True
                    transformation_info = {
                        'content_type': self.transformation.get('content_type', 'application/x-python'),
                        'content_source': self.transformation.get('content_source', 'inline'),
                        'input_mapping_applied': bool(input_mapping)
                    }
                except Exception as e:
                    # Return error but don't fail the entire connection
                    return {
                        "success": False,
                        "timestamp": timestamp,
                        "error_message": f"Transformation failed: {str(e)}",
                        "arrow_type": self.arrow_type,
                        "transformation_info": transformation_info
                    }
            
            # Load parameters into target widget
            for i, target_param in enumerate(self.target_parameters):
                if i < len(self.source_parameters):
                    source_param = self.source_parameters[i]
                    if source_param in transformed_data:
                        # Set input parameter in target widget
                        if hasattr(target_widget_instance, 'input_variables'):
                            target_widget_instance.input_variables[target_param] = transformed_data[source_param]
                        else:
                            setattr(target_widget_instance, target_param, transformed_data[source_param])
            
            return {
                "success": True,
                "timestamp": timestamp,
                "parameters_transferred": transformed_data,
                "transformation_applied": transformation_applied,
                "transformation_info": transformation_info,
                "arrow_type": self.arrow_type,
                "comment": self.comment
            }
            
        except Exception as e:
            return {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error_message": str(e),
                "arrow_type": self.arrow_type
            }
    
    def to_jsonld(self) -> Dict[str, Any]:
        """Convert arrow to JSON-LD representation"""
        jsonld = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/libraries/core/core.jsonld"
            ],
            "@id": f"urn:arrow:{self.source_widget}:{self.target_widget}",
            "@type": ["prov:Entity", "workflow:Connection"],
            "workflow:source": self.source_widget,
            "workflow:target": self.target_widget,
            "workflow:sourceParameters": self.source_parameters,
            "workflow:targetParameters": self.target_parameters,
            "workflow:connectionType": self.arrow_type,
            "rdfs:comment": self.comment,
            "workflow:hasTransformation": bool(self.transformation),
            "dct:created": datetime.now().isoformat()
        }
        
        # Add transformation info if present
        if self.transformation:
            transformation_jsonld = {
                "@type": ["prov:Entity", "workflow:Transformation"]
            }
            
            # Add content type
            if 'content_type' in self.transformation:
                transformation_jsonld["dct:format"] = self.transformation['content_type']
            
            # Add content source info
            if 'content_source' in self.transformation:
                transformation_jsonld["workflow:contentSource"] = self.transformation['content_source']
            
            jsonld["workflow:transformation"] = transformation_jsonld
        
        return jsonld