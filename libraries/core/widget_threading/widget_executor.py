"""
Threaded Widget Executor
Enhanced widget executor with threading support and lifecycle management
"""

import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import base widget from parent directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from base_widget import WidgetExecutor
from .thread_pool_engine import get_global_engine, WidgetStatus


class ThreadedWidgetExecutor(WidgetExecutor):
    """
    Enhanced widget executor with threading support and lifecycle management
    Extends base WidgetExecutor with run/stop/halt actions
    """
    
    def __init__(self, widget_schema: Dict[str, Any], jsonld_schema: Optional[Dict[str, Any]] = None):
        super().__init__(widget_schema, jsonld_schema)
        
        # Threading support
        self.thread_pool_engine = None
        self.current_task_id = None
        self.execution_thread = None
        self.is_running = False
        self.stop_requested = False
        self.halt_requested = False
        
        # Execution state
        self.execution_history: List[Dict[str, Any]] = []
        self.last_execution_result = None
        self.execution_count = 0
        
        # Add threading actions to base actions
        threading_actions = {
            'run': {
                'names': {'en': 'Run Widget'},
                'description': 'Start widget execution in thread pool',
                'output_format': 'json',
                'validation_required': True
            },
            'stop': {
                'names': {'en': 'Stop Widget'}, 
                'description': 'Gracefully stop widget execution',
                'output_format': 'json',
                'validation_required': False
            },
            'halt': {
                'names': {'en': 'Halt Widget'},
                'description': 'Forcefully halt widget execution',
                'output_format': 'json', 
                'validation_required': False
            },
            'get_status': {
                'names': {'en': 'Get Status'},
                'description': 'Get current widget execution status',
                'output_format': 'json',
                'validation_required': False
            }
        }
        
        # Merge with existing actions
        self.actions.update(threading_actions)
    
    def set_thread_pool_engine(self, engine):
        """Set the thread pool engine for this widget"""
        self.thread_pool_engine = engine
        
        # Register this widget with the engine
        engine.register_widget(self.id, self)
    
    def action_run(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run action - starts widget execution in thread pool
        """
        if self.is_running:
            return {
                'success': False,
                'error': 'Widget is already running',
                'widget_id': self.id,
                'status': 'running'
            }
        
        try:
            # Get or initialize thread pool engine
            if self.thread_pool_engine is None:
                self.thread_pool_engine = get_global_engine()
                if not self.thread_pool_engine.is_running:
                    self.thread_pool_engine.initialize()
                self.thread_pool_engine.register_widget(self.id, self)
            
            # Submit to thread pool
            self.current_task_id = self.thread_pool_engine.run_widget(
                widget_id=self.id,
                action='execute',
                input_data=validated_input,
                priority=validated_input.get('priority', 0)
            )
            
            self.is_running = True
            self.stop_requested = False
            self.halt_requested = False
            
            return {
                'success': True,
                'widget_id': self.id,
                'task_id': self.current_task_id,
                'status': 'queued',
                'message': 'Widget queued for execution',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'widget_id': self.id,
                'status': 'failed'
            }
    
    def action_stop(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop action - gracefully stops widget execution
        """
        if not self.is_running:
            return {
                'success': True,
                'widget_id': self.id,
                'status': 'not_running',
                'message': 'Widget is not currently running'
            }
        
        try:
            self.stop_requested = True
            
            if self.thread_pool_engine and self.current_task_id:
                stopped = self.thread_pool_engine.stop_widget(self.id)
            else:
                stopped = True
            
            self.is_running = False
            
            return {
                'success': True,
                'widget_id': self.id,
                'status': 'stopped',
                'stopped': stopped,
                'message': 'Widget execution stopped',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'widget_id': self.id,
                'status': 'error'
            }
    
    def action_halt(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Halt action - forcefully halts widget execution
        """
        try:
            self.halt_requested = True
            self.stop_requested = True
            
            if self.thread_pool_engine and self.current_task_id:
                halted = self.thread_pool_engine.halt_widget(self.id)
            else:
                halted = True
            
            self.is_running = False
            
            return {
                'success': True,
                'widget_id': self.id,
                'status': 'halted',
                'halted': halted,
                'message': 'Widget execution halted forcefully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'widget_id': self.id,
                'status': 'error'
            }
    
    def action_get_status(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get status action - returns current widget execution status
        """
        status_info = {
            'widget_id': self.id,
            'is_running': self.is_running,
            'stop_requested': self.stop_requested,
            'halt_requested': self.halt_requested,
            'execution_count': self.execution_count,
            'current_task_id': self.current_task_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get thread pool status if available
        if self.thread_pool_engine:
            widget_status = self.thread_pool_engine.get_widget_status(self.id)
            status_info.update(widget_status)
            
            # Get current task status
            if self.current_task_id:
                task_status = self.thread_pool_engine.get_task_status(self.current_task_id)
                if task_status:
                    status_info['current_task'] = task_status
        
        # Add execution history summary
        if self.execution_history:
            status_info['last_execution'] = self.execution_history[-1]
            status_info['total_executions'] = len(self.execution_history)
        
        return {
            'success': True,
            'status': status_info
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced execute method with threading support and stop/halt checking
        """
        # Check if we should stop/halt
        if self.stop_requested or self.halt_requested:
            return {
                'success': False,
                'error': 'Execution stopped by request',
                'widget_id': self.id,
                'halted': self.halt_requested
            }
        
        # Record execution start
        execution_start = {
            'execution_id': f"{self.id}_{datetime.now().timestamp()}",
            'started_at': datetime.now().isoformat(),
            'thread_id': threading.get_ident(),
            'input_data': input_data.copy() if input_data else {}
        }
        
        try:
            # Call parent execute method
            result = super().execute(input_data)
            
            # Record successful execution
            execution_start['completed_at'] = datetime.now().isoformat()
            execution_start['success'] = True
            execution_start['result_summary'] = {
                'success': result.get('success', False),
                'execution_time': result.get('execution_time', 0)
            }
            
            self.execution_count += 1
            self.last_execution_result = result
            
            # Update running status
            self.is_running = False
            
            return result
            
        except Exception as e:
            # Record failed execution
            execution_start['completed_at'] = datetime.now().isoformat()
            execution_start['success'] = False
            execution_start['error'] = str(e)
            
            self.is_running = False
            
            raise
            
        finally:
            # Always record execution in history
            self.execution_history.append(execution_start)
            
            # Keep only last 10 executions
            if len(self.execution_history) > 10:
                self.execution_history = self.execution_history[-10:]
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced implementation that respects stop/halt requests
        """
        # Check for stop/halt at regular intervals during execution
        if self.stop_requested:
            return {
                'success': False,
                'error': 'Execution stopped by request',
                'widget_id': self.id
            }
        
        if self.halt_requested:
            return {
                'success': False,  
                'error': 'Execution halted by request',
                'widget_id': self.id,
                'halted': True
            }
        
        # Call parent implementation 
        return super()._execute_impl(validated_input)
    
    def get_threading_stats(self) -> Dict[str, Any]:
        """Get threading-specific statistics"""
        return {
            'widget_id': self.id,
            'threading_enabled': True,
            'is_running': self.is_running,
            'execution_count': self.execution_count,
            'has_thread_pool': self.thread_pool_engine is not None,
            'current_task_id': self.current_task_id,
            'execution_history_count': len(self.execution_history),
            'stop_requested': self.stop_requested,
            'halt_requested': self.halt_requested
        }


def create_threaded_widget(widget_type: str, widget_schema: Dict[str, Any], 
                          jsonld_schema: Optional[Dict[str, Any]] = None,
                          thread_pool_engine=None) -> ThreadedWidgetExecutor:
    """
    Factory function to create threaded widgets
    """
    widget = ThreadedWidgetExecutor(widget_schema, jsonld_schema)
    
    if thread_pool_engine:
        widget.set_thread_pool_engine(thread_pool_engine)
    
    return widget