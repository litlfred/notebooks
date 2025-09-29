"""
Threaded Notebook Widget Implementation
Enhanced notebook widget with threading support and orchestration capabilities
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'widget_threading'))

from notebook_widget import NotebookWidget
from widget_threading.widget_executor import ThreadedWidgetExecutor
from widget_threading.thread_pool_engine import get_global_engine


class ThreadedNotebookWidget(ThreadedWidgetExecutor):
    """
    Enhanced notebook widget with threading support and orchestration capabilities
    Inherits from ThreadedWidgetExecutor for full lifecycle management
    """
    
    # Enable threading support
    supports_threading = True
    supports_hierarchical_execution = True
    
    # Override input/output variable declarations
    input_variables = {
        'notebook_data': {},
        'render_mode': 'windowed',  # 'windowed' or 'fullscreen'
        'show_panels': True,
        'panel_config': {
            'show_library': True,
            'show_controls': True,
            'library_collapsed': False
        },
        'orchestration_mode': 'sequential',  # 'sequential', 'parallel', 'hierarchical'
        'auto_run_widgets': False,
        'widget_execution_timeout': 30
    }
    
    output_variables = {
        'success': True,
        'widget_instances': {},  # Dictionary mapping widget IDs to their data IRIs
        'board_state': {},
        'rendered_mode': 'windowed',
        'orchestration_result': {},
        'execution_summary': {}
    }
    
    def __init__(self, widget_schema: Dict[str, Any], jsonld_schema: Optional[Dict[str, Any]] = None):
        super().__init__(widget_schema, jsonld_schema)
        
        # Notebook-specific threading state
        self.child_widgets: Dict[str, Any] = {}
        self.widget_dependencies: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        self.orchestration_mode = 'sequential'
        
        # Add notebook orchestration actions
        notebook_actions = {
            'render_notebook': {
                'names': {'en': 'Render Notebook'},
                'description': 'Render notebook as interactive board',
                'output_format': 'json',
                'validation_required': True
            },
            'run_all_widgets': {
                'names': {'en': 'Run All Widgets'},
                'description': 'Execute all widgets in the notebook',
                'output_format': 'json',
                'validation_required': False
            },
            'stop_all_widgets': {
                'names': {'en': 'Stop All Widgets'},
                'description': 'Stop all running widgets in the notebook',
                'output_format': 'json',
                'validation_required': False
            },
            'get_notebook_status': {
                'names': {'en': 'Get Notebook Status'},
                'description': 'Get comprehensive notebook execution status',
                'output_format': 'json',
                'validation_required': False
            },
            'orchestrate_execution': {
                'names': {'en': 'Orchestrate Execution'},
                'description': 'Execute widgets according to orchestration mode',
                'output_format': 'json',
                'validation_required': True
            }
        }
        
        # Merge with existing actions
        self.actions.update(notebook_actions)
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced notebook execution with threading support
        """
        notebook_data = validated_input.get('notebook_data', {})
        render_mode = validated_input.get('render_mode', 'windowed')
        orchestration_mode = validated_input.get('orchestration_mode', 'sequential')
        auto_run_widgets = validated_input.get('auto_run_widgets', False)
        
        self.orchestration_mode = orchestration_mode
        
        try:
            # Extract and register widgets from notebook
            result = self._process_notebook_widgets(notebook_data)
            
            # Set up orchestration if requested
            if auto_run_widgets:
                orchestration_result = self._orchestrate_widget_execution()
                result['orchestration_result'] = orchestration_result
            
            # Add rendering information
            result.update({
                'success': True,
                'rendered_mode': render_mode,
                'orchestration_mode': orchestration_mode,
                'total_widgets': len(self.child_widgets),
                'auto_run_enabled': auto_run_widgets
            })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Notebook execution failed: {str(e)}',
                'widget_instances': {},
                'board_state': {}
            }
    
    def _process_notebook_widgets(self, notebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and register widgets from notebook data"""
        graph = notebook_data.get('@graph', [])
        widgets = [item for item in graph if self._is_widget_entity(item)]
        
        widget_instances = {}
        
        # Get or initialize thread pool engine
        if self.thread_pool_engine is None:
            self.thread_pool_engine = get_global_engine()
            if not self.thread_pool_engine.is_running:
                self.thread_pool_engine.initialize()
        
        # Process each widget
        for widget_data in widgets:
            widget_id = widget_data.get('@id', '').replace('urn:widget:', '')
            if not widget_id:
                continue
            
            # Create widget instance (simplified for demo)
            widget_info = {
                'id': widget_id,
                'type': self._extract_widget_type(widget_data),
                'data': widget_data,
                'status': 'registered'
            }
            
            self.child_widgets[widget_id] = widget_info
            widget_instances[widget_id] = widget_data.get('@id')
            
            # Register with thread pool engine
            self.thread_pool_engine.register_widget(widget_id, self, parent_id=self.id)
        
        # Process dependencies (connections between widgets)
        connections = self._extract_connections(graph)
        self._build_dependency_graph(connections)
        
        return {
            'widget_instances': widget_instances,
            'board_state': {
                'title': notebook_data.get('dct:title', 'Untitled Notebook'),
                'description': notebook_data.get('dct:description', ''),
                'widgets': list(self.child_widgets.keys()),
                'connections': connections
            }
        }
    
    def _is_widget_entity(self, item: Dict[str, Any]) -> bool:
        """Check if an item is a widget entity"""
        types = item.get('@type', [])
        if isinstance(types, str):
            types = [types]
        
        widget_indicators = ['widget', 'Widget', 'prov:Entity']
        return any(indicator in str(types) for indicator in widget_indicators)
    
    def _extract_widget_type(self, widget_data: Dict[str, Any]) -> str:
        """Extract widget type from widget data"""
        types = widget_data.get('@type', [])
        if isinstance(types, str):
            types = [types]
        
        # Look for specific widget type patterns
        for type_str in types:
            if ':widget' in type_str:
                return type_str.replace(':widget', '')
            elif 'widget' in type_str.lower():
                return type_str
        
        return 'unknown'
    
    def _extract_connections(self, graph: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract connections from notebook graph"""
        connections = []
        
        for item in graph:
            if item.get('@type') == 'prov:Activity' or 'connection' in str(item.get('@type', '')).lower():
                # This is a connection/arrow
                connection = {
                    'id': item.get('@id', ''),
                    'source': item.get('prov:used', ''),
                    'target': item.get('prov:generated', ''),
                    'type': 'data_flow'
                }
                connections.append(connection)
        
        return connections
    
    def _build_dependency_graph(self, connections: List[Dict[str, Any]]):
        """Build widget dependency graph from connections"""
        self.widget_dependencies.clear()
        
        for connection in connections:
            source_id = connection.get('source', '').replace('urn:widget:', '')
            target_id = connection.get('target', '').replace('urn:widget:', '')
            
            if target_id and source_id:
                if target_id not in self.widget_dependencies:
                    self.widget_dependencies[target_id] = []
                self.widget_dependencies[target_id].append(source_id)
        
        # Calculate execution order based on dependencies
        self.execution_order = self._topological_sort()
    
    def _topological_sort(self) -> List[str]:
        """Calculate optimal execution order using topological sort"""
        # Simple topological sort implementation
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(widget_id: str):
            if widget_id in temp_visited:
                # Circular dependency detected - use original order
                return
            if widget_id in visited:
                return
            
            temp_visited.add(widget_id)
            
            # Visit dependencies first
            for dep_id in self.widget_dependencies.get(widget_id, []):
                if dep_id in self.child_widgets:
                    visit(dep_id)
            
            temp_visited.remove(widget_id)
            visited.add(widget_id)
            result.append(widget_id)
        
        # Visit all widgets
        for widget_id in self.child_widgets.keys():
            if widget_id not in visited:
                visit(widget_id)
        
        return result
    
    def _orchestrate_widget_execution(self) -> Dict[str, Any]:
        """Orchestrate widget execution based on orchestration mode"""
        if not self.thread_pool_engine:
            return {
                'success': False,
                'error': 'Thread pool engine not available'
            }
        
        try:
            if self.orchestration_mode == 'sequential':
                return self._execute_sequential()
            elif self.orchestration_mode == 'parallel':
                return self._execute_parallel()
            elif self.orchestration_mode == 'hierarchical':
                return self._execute_hierarchical()
            else:
                return {
                    'success': False,
                    'error': f'Unknown orchestration mode: {self.orchestration_mode}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Orchestration failed: {str(e)}'
            }
    
    def _execute_sequential(self) -> Dict[str, Any]:
        """Execute widgets sequentially in dependency order"""
        task_ids = []
        
        for widget_id in self.execution_order:
            if widget_id in self.child_widgets:
                task_id = self.thread_pool_engine.run_widget(widget_id, 'execute')
                task_ids.append(task_id)
        
        return {
            'success': True,
            'mode': 'sequential',
            'task_ids': task_ids,
            'execution_order': self.execution_order
        }
    
    def _execute_parallel(self) -> Dict[str, Any]:
        """Execute all widgets in parallel"""
        task_ids = []
        
        for widget_id in self.child_widgets.keys():
            task_id = self.thread_pool_engine.run_widget(widget_id, 'execute')
            task_ids.append(task_id)
        
        return {
            'success': True,
            'mode': 'parallel',
            'task_ids': task_ids,
            'total_widgets': len(task_ids)
        }
    
    def _execute_hierarchical(self) -> Dict[str, Any]:
        """Execute widgets hierarchically using thread pool engine"""
        # Find root widgets (widgets with no dependencies)
        root_widgets = [
            widget_id for widget_id in self.child_widgets.keys()
            if widget_id not in self.widget_dependencies or not self.widget_dependencies[widget_id]
        ]
        
        all_task_ids = []
        
        for root_widget_id in root_widgets:
            task_ids = self.thread_pool_engine.run_hierarchical(root_widget_id)
            all_task_ids.extend(task_ids)
        
        return {
            'success': True,
            'mode': 'hierarchical',
            'root_widgets': root_widgets,
            'task_ids': all_task_ids,
            'total_tasks': len(all_task_ids)
        }
    
    # Action implementations
    def action_render_notebook(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to render notebook"""
        return self.execute(validated_input)
    
    def action_run_all_widgets(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to run all widgets in the notebook"""
        try:
            if not self.child_widgets:
                return {
                    'success': False,
                    'error': 'No widgets loaded in notebook'
                }
            
            orchestration_result = self._orchestrate_widget_execution()
            
            return {
                'success': True,
                'action': 'run_all_widgets',
                'total_widgets': len(self.child_widgets),
                'orchestration_mode': self.orchestration_mode,
                'result': orchestration_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'run_all_widgets'
            }
    
    def action_stop_all_widgets(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to stop all widgets in the notebook"""
        try:
            stopped_widgets = []
            
            for widget_id in self.child_widgets.keys():
                if self.thread_pool_engine:
                    stopped = self.thread_pool_engine.stop_widget(widget_id)
                    if stopped:
                        stopped_widgets.append(widget_id)
            
            return {
                'success': True,
                'action': 'stop_all_widgets',
                'stopped_widgets': stopped_widgets,
                'total_stopped': len(stopped_widgets)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'stop_all_widgets'
            }
    
    def action_get_notebook_status(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to get comprehensive notebook status"""
        try:
            widget_statuses = {}
            
            # Get status for each child widget  
            for widget_id in self.child_widgets.keys():
                if self.thread_pool_engine:
                    status = self.thread_pool_engine.get_widget_status(widget_id)
                    widget_statuses[widget_id] = status
            
            # Get overall notebook threading stats
            notebook_threading_stats = self.get_threading_stats()
            
            return {
                'success': True,
                'notebook_id': self.id,
                'orchestration_mode': self.orchestration_mode,
                'total_widgets': len(self.child_widgets),
                'execution_order': self.execution_order,
                'dependencies': self.widget_dependencies,
                'widget_statuses': widget_statuses,
                'notebook_threading': notebook_threading_stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'get_notebook_status'
            }
    
    def action_orchestrate_execution(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to orchestrate widget execution with specific mode"""
        try:
            # Update orchestration mode if provided
            if 'orchestration_mode' in validated_input:
                self.orchestration_mode = validated_input['orchestration_mode']
            
            result = self._orchestrate_widget_execution()
            
            return {
                'success': True,
                'action': 'orchestrate_execution',
                'orchestration_mode': self.orchestration_mode,
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'orchestrate_execution'
            }


def create_threaded_notebook_widget(widget_schema: Dict[str, Any], 
                                   jsonld_schema: Optional[Dict[str, Any]] = None,
                                   thread_pool_engine=None) -> ThreadedNotebookWidget:
    """
    Factory function to create threaded notebook widgets
    """
    widget = ThreadedNotebookWidget(widget_schema, jsonld_schema)
    
    if thread_pool_engine:
        widget.set_thread_pool_engine(thread_pool_engine)
    
    return widget