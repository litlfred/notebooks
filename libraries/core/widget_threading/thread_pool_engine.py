"""
Thread Pool Engine for Widget Execution
Manages threaded execution of widgets with proper isolation and communication
"""

import asyncio
import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .context_manager import ExecutionContext


class WidgetStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    HALTED = "halted"


@dataclass
class WidgetTask:
    """Represents a widget execution task"""
    widget_id: str
    action: str
    input_data: Dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    status: WidgetStatus = WidgetStatus.QUEUED
    future: Optional[Future] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    thread_id: Optional[int] = None


class ThreadPoolEngine:
    """
    Thread pool engine for executing widgets with proper isolation and hierarchy support
    """
    
    def __init__(self, max_workers: int = 4, enable_lazy_loading: bool = True):
        self.max_workers = max_workers
        self.enable_lazy_loading = enable_lazy_loading
        
        # Thread pool for widget execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="widget")
        
        # Task management
        self.tasks: Dict[str, WidgetTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, WidgetTask] = {}
        
        # Widget registry and hierarchy
        self.widgets: Dict[str, Any] = {}  # widget_id -> widget instance
        self.widget_hierarchy: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
        self.widget_dependencies: Dict[str, List[str]] = {}  # widget_id -> [dependency_ids]
        
        # Execution context management
        self.execution_context = ExecutionContext(lazy_loading=enable_lazy_loading)
        
        # Status tracking
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Communication channels
        self.result_callbacks: Dict[str, List[Callable]] = {}
        self.status_callbacks: Dict[str, List[Callable]] = {}
        
    def initialize(self):
        """Initialize the thread pool engine and execution context"""
        try:
            self.logger.info(f"Initializing ThreadPoolEngine with {self.max_workers} workers")
            
            # Initialize execution context (loads Python libraries, etc.)
            self.execution_context.initialize()
            
            self.is_running = True
            self.logger.info("ThreadPoolEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ThreadPoolEngine: {e}")
            raise
    
    def register_widget(self, widget_id: str, widget_instance: Any, parent_id: Optional[str] = None):
        """Register a widget with the engine"""
        self.widgets[widget_id] = widget_instance
        
        # Set up hierarchy if parent specified
        if parent_id:
            if parent_id not in self.widget_hierarchy:
                self.widget_hierarchy[parent_id] = []
            self.widget_hierarchy[parent_id].append(widget_id)
            
        self.logger.debug(f"Registered widget {widget_id} with parent {parent_id}")
    
    def add_widget_dependency(self, widget_id: str, dependency_id: str):
        """Add a dependency relationship between widgets"""
        if widget_id not in self.widget_dependencies:
            self.widget_dependencies[widget_id] = []
        self.widget_dependencies[widget_id].append(dependency_id)
        
    def run_widget(self, widget_id: str, action: str = "execute", 
                   input_data: Optional[Dict[str, Any]] = None, 
                   priority: int = 0) -> str:
        """
        Queue a widget for execution
        Returns task_id for tracking
        """
        if not self.is_running:
            raise RuntimeError("ThreadPoolEngine is not running")
            
        if widget_id not in self.widgets:
            raise ValueError(f"Widget {widget_id} not registered")
        
        # Create task
        task_id = f"{widget_id}_{action}_{datetime.now().timestamp()}"
        task = WidgetTask(
            widget_id=widget_id,
            action=action,
            input_data=input_data or {},
            priority=priority
        )
        
        self.tasks[task_id] = task
        
        # Submit to thread pool
        future = self.executor.submit(self._execute_widget_task, task_id)
        task.future = future
        
        self.logger.info(f"Queued widget {widget_id} for execution with task_id {task_id}")
        return task_id
    
    def run_hierarchical(self, root_widget_id: str, action: str = "execute") -> List[str]:
        """
        Run a widget and all its children hierarchically
        Returns list of task_ids in execution order
        """
        task_ids = []
        
        # Execute dependencies first
        if root_widget_id in self.widget_dependencies:
            for dep_id in self.widget_dependencies[root_widget_id]:
                dep_task_ids = self.run_hierarchical(dep_id, action)
                task_ids.extend(dep_task_ids)
        
        # Execute root widget
        root_task_id = self.run_widget(root_widget_id, action, priority=1)
        task_ids.append(root_task_id)
        
        # Execute children after root completes
        if root_widget_id in self.widget_hierarchy:
            for child_id in self.widget_hierarchy[root_widget_id]:
                child_task_ids = self.run_hierarchical(child_id, action)
                task_ids.extend(child_task_ids)
        
        return task_ids
    
    def stop_widget(self, widget_id: str) -> bool:
        """Stop all running tasks for a widget"""
        stopped = False
        
        # Find and cancel active tasks for this widget
        for task_id, task in list(self.active_tasks.items()):
            if task.widget_id == widget_id:
                if task.future and not task.future.done():
                    task.future.cancel()
                    task.status = WidgetStatus.CANCELLED
                    stopped = True
                    
        self.logger.info(f"Stopped widget {widget_id}")
        return stopped
    
    def halt_widget(self, widget_id: str) -> bool:
        """Forcefully halt a widget (more aggressive than stop)"""
        # First try graceful stop
        stopped = self.stop_widget(widget_id)
        
        # Mark widget as halted
        for task_id, task in self.tasks.items():
            if task.widget_id == widget_id and task.status == WidgetStatus.RUNNING:
                task.status = WidgetStatus.HALTED
                
        self.logger.warning(f"Halted widget {widget_id}")
        return stopped
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            'task_id': task_id,
            'widget_id': task.widget_id,
            'action': task.action,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'thread_id': task.thread_id,
            'has_result': task.result is not None,
            'has_error': task.error is not None
        }
    
    def get_widget_status(self, widget_id: str) -> Dict[str, Any]:
        """Get comprehensive status for a widget"""
        widget_tasks = [task for task in self.tasks.values() if task.widget_id == widget_id]
        
        return {
            'widget_id': widget_id,
            'is_registered': widget_id in self.widgets,
            'total_tasks': len(widget_tasks),
            'active_tasks': len([t for t in widget_tasks if t.status == WidgetStatus.RUNNING]),
            'completed_tasks': len([t for t in widget_tasks if t.status == WidgetStatus.COMPLETED]),
            'failed_tasks': len([t for t in widget_tasks if t.status == WidgetStatus.FAILED]),
            'children': self.widget_hierarchy.get(widget_id, []),
            'dependencies': self.widget_dependencies.get(widget_id, [])
        }
    
    def add_result_callback(self, widget_id: str, callback: Callable):
        """Add callback to be called when widget completes"""
        if widget_id not in self.result_callbacks:
            self.result_callbacks[widget_id] = []
        self.result_callbacks[widget_id].append(callback)
    
    def _execute_widget_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a widget task in a thread"""
        task = self.tasks[task_id]
        task.status = WidgetStatus.RUNNING
        task.thread_id = threading.get_ident()
        
        self.active_tasks[task_id] = task
        
        try:
            self.logger.debug(f"Executing task {task_id} for widget {task.widget_id}")
            
            # Get widget instance
            widget = self.widgets[task.widget_id]
            
            # Execute widget action
            if task.action == "execute":
                result = widget.execute(task.input_data)
            elif hasattr(widget, f"action_{task.action}"):
                action_method = getattr(widget, f"action_{task.action}")
                result = action_method(task.input_data)
            elif hasattr(widget, "execute_action"):
                result = widget.execute_action(task.input_data, task.action)
            else:
                raise ValueError(f"Action '{task.action}' not supported by widget {task.widget_id}")
            
            # Store result
            task.result = result
            task.status = WidgetStatus.COMPLETED
            
            # Call result callbacks
            if task.widget_id in self.result_callbacks:
                for callback in self.result_callbacks[task.widget_id]:
                    try:
                        callback(task.widget_id, result)
                    except Exception as e:
                        self.logger.error(f"Callback error for widget {task.widget_id}: {e}")
            
            self.logger.debug(f"Task {task_id} completed successfully")
            return result
            
        except Exception as e:
            task.error = e
            task.status = WidgetStatus.FAILED
            self.logger.error(f"Task {task_id} failed: {e}")
            raise
            
        finally:
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = None):
        """Shutdown the thread pool engine"""
        self.logger.info("Shutting down ThreadPoolEngine")
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Cancel all pending tasks
        for task in self.active_tasks.values():
            if task.future and not task.future.done():
                task.future.cancel()
        
        # Shutdown thread pool - handle Python version differences
        try:
            # Try Python 3.9+ signature first
            self.executor.shutdown(wait=wait, timeout=timeout)
        except TypeError:
            # Fall back to older Python versions
            self.executor.shutdown(wait=wait)
        
        # Cleanup execution context
        self.execution_context.cleanup()
        
        self.logger.info("ThreadPoolEngine shutdown complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            'max_workers': self.max_workers,
            'is_running': self.is_running,
            'total_widgets': len(self.widgets),
            'total_tasks': len(self.tasks),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len([t for t in self.tasks.values() if t.status == WidgetStatus.COMPLETED]),
            'failed_tasks': len([t for t in self.tasks.values() if t.status == WidgetStatus.FAILED]),
            'context_initialized': self.execution_context.is_initialized
        }


# Global thread pool engine instance
_global_engine = None

def get_global_engine() -> ThreadPoolEngine:
    """Get the global thread pool engine instance"""
    global _global_engine
    if _global_engine is None:
        _global_engine = ThreadPoolEngine()
    return _global_engine

def initialize_global_engine(max_workers: int = 4):
    """Initialize the global thread pool engine"""
    global _global_engine
    _global_engine = ThreadPoolEngine(max_workers=max_workers)
    _global_engine.initialize()
    return _global_engine