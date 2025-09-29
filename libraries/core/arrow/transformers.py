"""
Multi-Type Transformation System
Base classes and factory for supporting multiple transformation languages
"""

import subprocess
import json
import tempfile
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional


class BaseTransformer(ABC):
    """Base class for all transformation language implementations"""
    
    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """Return list of MIME types this transformer supports"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate transformation content syntax and structure"""
        pass
    
    @abstractmethod
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Compile transformation content into executable function"""
        pass
    
    @abstractmethod
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute compiled transformation function"""
        pass


class TransformerFactory:
    """Factory for managing transformer implementations"""
    
    _transformers: Dict[str, BaseTransformer] = {}
    
    @classmethod
    def register_transformer(cls, transformer: BaseTransformer):
        """Register a new transformer implementation"""
        for mime_type in transformer.get_supported_mime_types():
            cls._transformers[mime_type] = transformer
    
    @classmethod
    def get_transformer(cls, content_type: str) -> BaseTransformer:
        """Get transformer for specified content type"""
        if content_type not in cls._transformers:
            raise ValueError(f"No transformer registered for content type: {content_type}")
        return cls._transformers[content_type]
    
    @classmethod
    def list_supported_types(cls) -> List[str]:
        """List all supported MIME types"""
        return list(cls._transformers.keys())
    
    @classmethod
    def is_supported(cls, content_type: str) -> bool:
        """Check if content type is supported"""
        return content_type in cls._transformers


class PythonTransformer(BaseTransformer):
    """Built-in Python transformation support"""
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/x-python', 'text/x-python']
    
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate Python syntax"""
        try:
            compile(content, '<transformation>', 'exec')
            return True
        except SyntaxError:
            return False
    
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Compile Python transformation code"""
        # Check if the content looks like a complete function or just code body
        content = content.strip()
        
        if content.startswith('def ') and 'transform_parameters' in content:
            # Content is already a complete function definition
            function_code = content
        else:
            # Content is just the function body, wrap it
            # Indent each line of content
            indented_content = '\n'.join('    ' + line for line in content.split('\n'))
            function_code = f"""
def transform_parameters(source_data, input_mapping=None):
    '''User-defined transformation function'''
{indented_content}
    return source_data
"""
        
        try:
            local_scope = {}
            exec(function_code, {"__builtins__": __builtins__}, local_scope)
            return local_scope['transform_parameters']
        except Exception as e:
            raise ValueError(f"Failed to compile Python transformation: {e}")
    
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute Python transformation"""
        try:
            return compiled_function(source_data, input_mapping)
        except Exception as e:
            raise RuntimeError(f"Python transformation execution failed: {e}")


class NodeExecutor:
    """Handles communication with Node.js transformer processes"""
    
    def __init__(self):
        self.transformers_path = Path(__file__).parent / "transformers"
        self.ensure_transformers_directory()
    
    def ensure_transformers_directory(self):
        """Ensure transformers directory exists"""
        self.transformers_path.mkdir(exist_ok=True)
        
        # Create package.json if it doesn't exist
        package_json_path = self.transformers_path / "package.json"
        if not package_json_path.exists():
            package_json = {
                "name": "notebooks-transformers",
                "version": "1.0.0",
                "description": "Node.js transformers for notebook widget arrows",
                "main": "index.js",
                "dependencies": {}
            }
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)
    
    def validate(self, package_name: str, module_path: str, content: str, 
                 config: Dict[str, Any]) -> bool:
        """Validate transformation content using Node.js module"""
        # Use absolute path for require
        module_abs_path = str(self.transformers_path / package_name / module_path)
        validation_script = f"""
try {{
    const transformer = require('{module_abs_path}');
    const content = {json.dumps(content)};
    const config = {json.dumps(config)};
    
    const isValid = transformer.validate(content, config);
    console.log(JSON.stringify({{ success: true, valid: isValid }}));
}} catch (error) {{
    console.log(JSON.stringify({{ success: false, error: error.message }}));
}}
"""
        result = self._run_node_script(validation_script)
        return result.get('success', False) and result.get('valid', False)
    
    def execute(self, package_name: str, module_path: str, content: str,
                source_data: Dict[str, Any], input_mapping: Dict[str, str],
                config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation using Node.js module"""
        # Use absolute path for require
        module_abs_path = str(self.transformers_path / package_name / module_path)
        execution_script = f"""
try {{
    const transformer = require('{module_abs_path}');
    const content = {json.dumps(content)};
    const sourceData = {json.dumps(source_data)};
    const inputMapping = {json.dumps(input_mapping)};
    const config = {json.dumps(config)};
    
    const result = transformer.transform(content, sourceData, inputMapping, config);
    console.log(JSON.stringify({{ success: true, result: result }}));
}} catch (error) {{
    console.log(JSON.stringify({{ success: false, error: error.message, stack: error.stack }}));
}}
"""
        result = self._run_node_script(execution_script)
        if result.get('success', False):
            return result.get('result', source_data)
        else:
            error_msg = result.get('error', 'Unknown error')
            raise RuntimeError(f"Node.js transformation failed: {error_msg}")
    
    def _run_node_script(self, script: str) -> Dict[str, Any]:
        """Execute Node.js script and return parsed JSON result"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute Node.js script with proper PATH and timeout
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.transformers_path
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    # Handle case where there might be console.log output before the JSON
                    lines = output.split('\n')
                    for line in reversed(lines):
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                return json.loads(line)
                            except json.JSONDecodeError:
                                continue
                    # If no valid JSON found, try the last line
                    try:
                        return json.loads(lines[-1])
                    except json.JSONDecodeError:
                        return {"success": False, "error": f"No valid JSON found in output: {output}"}
                else:
                    return {"success": False, "error": "No output from Node.js script"}
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return {"success": False, "error": f"Node.js script failed: {error_msg}"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Transformation timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Node.js not found. Please install Node.js to use non-Python transformers."}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}
        finally:
            try:
                os.unlink(script_path)
            except:
                pass  # Ignore cleanup errors


class NodeJSTransformer(BaseTransformer):
    """Base class for Node.js-based transformers"""
    
    def __init__(self, package_name: str, module_path: str):
        self.package_name = package_name
        self.module_path = module_path
        self.node_executor = NodeExecutor()
    
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate content using Node.js module"""
        try:
            return self.node_executor.validate(
                self.package_name, 
                self.module_path, 
                content, 
                transformation_config
            )
        except Exception:
            return False
    
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Return a callable that will execute via Node.js"""
        def node_transformation(source_data: Dict[str, Any], input_mapping: Dict[str, str] = None):
            return self.node_executor.execute(
                self.package_name,
                self.module_path,
                content,
                source_data,
                input_mapping or {},
                transformation_config
            )
        return node_transformation
    
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute Node.js transformation"""
        return compiled_function(source_data, input_mapping)


# Register built-in Python transformer
TransformerFactory.register_transformer(PythonTransformer())