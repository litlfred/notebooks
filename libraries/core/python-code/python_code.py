"""
Python Code Widget Implementation
Interactive Python code execution widget for mathematical workflows
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from base_widget import WidgetExecutor
from typing import Dict, Any
import io
import contextlib

class PythonCodeWidget(WidgetExecutor):
    """
    Python code execution widget for interactive computational workflows.
    
    Input: Python code, imports, and variables
    Output: Execution result, stdout, stderr, and performance metrics
    """
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        code = validated_input.get('code', '')
        imports = validated_input.get('imports', [])
        variables = validated_input.get('variables', {})
        
        # Create execution context
        exec_globals = {'__builtins__': __builtins__}
        exec_globals.update(variables)
        
        # Capture stdout and stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            # Execute imports first
            for import_stmt in imports:
                exec(import_stmt, exec_globals)
            
            # Execute main code
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                exec_result = exec(code, exec_globals)
                
            return {
                'success': True,
                'result': exec_result,
                'stdout': stdout_buffer.getvalue(),
                'stderr': stderr_buffer.getvalue(),
                'variables_created': {k: str(v) for k, v in exec_globals.items() 
                                   if k not in {'__builtins__'} and not k.startswith('__')},
                'code_executed': code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'stdout': stdout_buffer.getvalue(),
                'stderr': stderr_buffer.getvalue(),
                'code_executed': code
            }

def create_python_code_widget(widget_schema: Dict[str, Any]) -> PythonCodeWidget:
    """Factory function to create python code widget instance"""
    return PythonCodeWidget(widget_schema)