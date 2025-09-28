"""
Workflow Arrow Implementation
Represents connections between widgets with optional ETL transformations
"""

import json
import inspect
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable


class WorkflowArrow:
    """
    Represents a connection arrow between widgets with optional transformation logic.
    Supports ETL (Extract, Transform, Load) pattern for parameter flow.
    """
    
    def __init__(self, arrow_config: Dict[str, Any]):
        self.source_widget = arrow_config['source_widget']
        self.target_widget = arrow_config['target_widget'] 
        self.source_parameters = arrow_config['source_parameters']
        self.target_parameters = arrow_config['target_parameters']
        self.arrow_type = arrow_config.get('arrow_type', 'parameter_flow')
        self.comment = arrow_config.get('comment', '')
        self.transformation = arrow_config.get('transformation', {})
        
        # Compile optional Python transformation function
        self.transform_function = None
        if 'python_code' in self.transformation:
            self._compile_transformation()
    
    def _compile_transformation(self):
        """Compile optional Python transformation code into executable function"""
        python_code = self.transformation['python_code']
        
        # Create transformation function with proper signature
        function_code = f"""
def transform_parameters(source_data, input_mapping=None):
    '''User-defined transformation function'''
    {python_code}
    return source_data
"""
        
        try:
            # Compile and execute the function definition
            local_scope = {}
            exec(function_code, {"__builtins__": __builtins__}, local_scope)
            self.transform_function = local_scope['transform_parameters']
        except Exception as e:
            raise ValueError(f"Failed to compile transformation function: {e}")
    
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
            transformed_data = source_data
            transformation_applied = False
            
            if self.transform_function:
                input_mapping = self.transformation.get('input_mapping', {})
                transformed_data = self.transform_function(source_data, input_mapping)
                transformation_applied = True
            
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
        return {
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