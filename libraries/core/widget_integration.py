"""
Widget Integration Layer
Connects JavaScript frontend with Python threading backend
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from widget_threading.thread_pool_engine import ThreadPoolEngine, get_global_engine
from widget_threading.widget_executor import create_threaded_widget
from base_widget import create_widget

class WidgetIntegrationManager:
    """
    Manages integration between JavaScript frontend and Python widget system
    """
    
    def __init__(self, thread_pool_config: Optional[Dict[str, Any]] = None):
        self.thread_pool_config = thread_pool_config or {
            'max_workers': 4,
            'enable_lazy_loading': True
        }
        
        self.engine: Optional[ThreadPoolEngine] = None
        self.registered_widgets: Dict[str, Any] = {}
        self.widget_schemas: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the integration manager and thread pool"""
        try:
            self.logger.info("Initializing Widget Integration Manager")
            
            # Initialize thread pool engine
            self.engine = ThreadPoolEngine(
                max_workers=self.thread_pool_config['max_workers'],
                enable_lazy_loading=self.thread_pool_config.get('enable_lazy_loading', True)
            )
            self.engine.initialize()
            
            return {
                'success': True,
                'message': 'Widget integration manager initialized',
                'thread_pool_stats': self.engine.get_stats(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integration manager: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def register_widget_schema(self, widget_type: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Register a widget schema for later instantiation"""
        try:
            self.widget_schemas[widget_type] = schema
            
            self.logger.debug(f"Registered widget schema for type: {widget_type}")
            
            return {
                'success': True,
                'widget_type': widget_type,
                'message': f'Widget schema {widget_type} registered'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'widget_type': widget_type
            }
    
    def create_widget_instance(self, widget_id: str, widget_type: str, 
                             config: Optional[Dict[str, Any]] = None,
                             enable_threading: bool = True) -> Dict[str, Any]:
        """Create a widget instance from registered schema"""
        try:
            if widget_type not in self.widget_schemas:
                raise ValueError(f"Widget type {widget_type} not registered")
            
            schema = self.widget_schemas[widget_type].copy()
            schema['id'] = widget_id
            
            # Create widget
            if enable_threading and self.engine:
                widget = create_threaded_widget(widget_type, schema, thread_pool_engine=self.engine)
            else:
                widget = create_widget(widget_type, schema)
            
            # Register with engine if threaded
            if enable_threading and self.engine:
                self.engine.register_widget(widget_id, widget)
            
            self.registered_widgets[widget_id] = widget
            
            self.logger.info(f"Created widget instance: {widget_id} (type: {widget_type})")
            
            return {
                'success': True,
                'widget_id': widget_id,
                'widget_type': widget_type,
                'threading_enabled': enable_threading,
                'actions': list(widget.actions.keys()),
                'message': f'Widget {widget_id} created successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create widget {widget_id}: {e}")
            return {
                'success': False,
                'widget_id': widget_id,
                'error': str(e)
            }
    
    def execute_widget_action(self, widget_id: str, action: str, 
                            input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an action on a widget"""
        try:
            if widget_id not in self.registered_widgets:
                raise ValueError(f"Widget {widget_id} not found")
            
            widget = self.registered_widgets[widget_id]
            input_data = input_data or {}
            
            # Execute action
            if action == 'execute':
                result = widget.execute(input_data)
            else:
                result = widget.execute_action(input_data, action)
            
            self.logger.debug(f"Executed action {action} on widget {widget_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute action {action} on widget {widget_id}: {e}")
            return {
                'success': False,
                'widget_id': widget_id,
                'action': action,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_widget_status(self, widget_id: str) -> Dict[str, Any]:
        """Get comprehensive status for a widget"""
        try:
            if widget_id not in self.registered_widgets:
                return {
                    'success': False,
                    'error': f'Widget {widget_id} not found'
                }
            
            widget = self.registered_widgets[widget_id]
            
            # Base status
            status = {
                'widget_id': widget_id,
                'exists': True,
                'widget_type': widget.schema.get('category', 'unknown'),
                'actions': list(widget.actions.keys())
            }
            
            # Add threading info if available
            if hasattr(widget, 'get_threading_stats'):
                status['threading'] = widget.get_threading_stats()
            
            # Add engine status if available
            if self.engine:
                engine_status = self.engine.get_widget_status(widget_id)
                status['engine'] = engine_status
            
            return {
                'success': True,
                'status': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'widget_id': widget_id,
                'error': str(e)
            }
    
    def stop_widget(self, widget_id: str) -> Dict[str, Any]:
        """Stop a widget"""
        try:
            if widget_id not in self.registered_widgets:
                return {
                    'success': False,
                    'error': f'Widget {widget_id} not found'
                }
            
            widget = self.registered_widgets[widget_id]
            
            # Try widget's stop action first
            if 'stop' in widget.actions:
                result = widget.execute_action({}, 'stop')
            else:
                # Fall back to engine stop
                if self.engine:
                    stopped = self.engine.stop_widget(widget_id)
                    result = {
                        'success': True,
                        'widget_id': widget_id,
                        'stopped': stopped,
                        'message': 'Widget stopped via engine'
                    }
                else:
                    result = {
                        'success': True,
                        'widget_id': widget_id,
                        'message': 'Widget does not support stopping'
                    }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'widget_id': widget_id,
                'error': str(e)
            }
    
    def halt_widget(self, widget_id: str) -> Dict[str, Any]:
        """Halt a widget forcefully"""
        try:
            if widget_id not in self.registered_widgets:
                return {
                    'success': False,
                    'error': f'Widget {widget_id} not found'
                }
            
            widget = self.registered_widgets[widget_id]
            
            # Try widget's halt action first
            if 'halt' in widget.actions:
                result = widget.execute_action({}, 'halt')
            else:
                # Fall back to engine halt
                if self.engine:
                    halted = self.engine.halt_widget(widget_id)
                    result = {
                        'success': True,
                        'widget_id': widget_id,
                        'halted': halted,
                        'message': 'Widget halted via engine'
                    }
                else:
                    result = {
                        'success': True,
                        'widget_id': widget_id,
                        'message': 'Widget does not support halting'
                    }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'widget_id': widget_id,
                'error': str(e)
            }
    
    def run_hierarchical(self, root_widget_id: str, action: str = 'execute') -> Dict[str, Any]:
        """Run hierarchical widget execution"""
        try:
            if not self.engine:
                raise ValueError("Thread pool engine not initialized")
            
            if root_widget_id not in self.registered_widgets:
                raise ValueError(f"Root widget {root_widget_id} not found")
            
            # Run hierarchical execution
            task_ids = self.engine.run_hierarchical(root_widget_id, action)
            
            return {
                'success': True,
                'root_widget_id': root_widget_id,
                'action': action,
                'task_ids': task_ids,
                'message': f'Hierarchical execution started for {root_widget_id}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'root_widget_id': root_widget_id,
                'error': str(e)
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            'integration_manager': {
                'registered_widgets': len(self.registered_widgets),
                'registered_schemas': len(self.widget_schemas),
                'thread_pool_initialized': self.engine is not None
            }
        }
        
        if self.engine:
            stats['thread_pool'] = self.engine.get_stats()
            stats['execution_context'] = self.engine.execution_context.get_stats()
        
        return stats
    
    def shutdown(self) -> Dict[str, Any]:
        """Shutdown the integration manager"""
        try:
            self.logger.info("Shutting down Widget Integration Manager")
            
            # Stop all widgets
            for widget_id in list(self.registered_widgets.keys()):
                self.stop_widget(widget_id)
            
            # Shutdown engine
            if self.engine:
                self.engine.shutdown()
            
            # Clear registrations
            self.registered_widgets.clear()
            self.widget_schemas.clear()
            
            return {
                'success': True,
                'message': 'Widget integration manager shutdown complete',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global integration manager instance
_global_manager = None

def get_global_integration_manager() -> WidgetIntegrationManager:
    """Get the global integration manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = WidgetIntegrationManager()
    return _global_manager

def initialize_global_integration_manager(config: Optional[Dict[str, Any]] = None):
    """Initialize the global integration manager"""
    global _global_manager
    _global_manager = WidgetIntegrationManager(config)
    return _global_manager.initialize()