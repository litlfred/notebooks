"""
Execution Context Manager for Widget Threading
Handles initialization of Python libraries and dependencies with lazy loading
"""

import sys
import importlib
import logging
from typing import Dict, Any, List, Optional, Set
from concurrent.futures import Future
import threading
import time


class LazyLoader:
    """Lazy loading utility for Python modules and dependencies"""
    
    def __init__(self):
        self.loaded_modules: Set[str] = set()
        self.loading_futures: Dict[str, Future] = {}
        self.load_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def load_module_async(self, module_name: str, required: bool = True) -> Future:
        """Load a module asynchronously"""
        with self.load_lock:
            if module_name in self.loaded_modules:
                # Already loaded, return completed future
                future = Future()
                future.set_result(sys.modules.get(module_name))
                return future
            
            if module_name in self.loading_futures:
                # Already loading, return existing future
                return self.loading_futures[module_name]
            
            # Start loading
            future = Future()
            self.loading_futures[module_name] = future
            
            def load():
                try:
                    module = importlib.import_module(module_name)
                    self.loaded_modules.add(module_name)
                    future.set_result(module)
                    self.logger.debug(f"Loaded module {module_name}")
                except ImportError as e:
                    if required:
                        future.set_exception(e)
                        self.logger.error(f"Failed to load required module {module_name}: {e}")
                    else:
                        future.set_result(None)
                        self.logger.warning(f"Optional module {module_name} not available: {e}")
                finally:
                    with self.load_lock:
                        if module_name in self.loading_futures:
                            del self.loading_futures[module_name]
            
            # Load in separate thread to avoid blocking
            threading.Thread(target=load, daemon=True).start()
            return future
    
    def wait_for_modules(self, module_names: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for multiple modules to load"""
        futures = {name: self.load_module_async(name) for name in module_names}
        results = {}
        
        for name, future in futures.items():
            try:
                results[name] = future.result(timeout=timeout)
            except Exception as e:
                results[name] = None
                self.logger.error(f"Failed to load module {name}: {e}")
        
        return results
    
    def preload_scientific_stack(self):
        """Preload common scientific computing modules"""
        scientific_modules = [
            'numpy',
            'matplotlib',
            'matplotlib.pyplot', 
            'scipy',
            'sympy',
            'pandas'
        ]
        
        self.logger.info("Preloading scientific computing stack...")
        
        # Load numpy first (many others depend on it)
        numpy_future = self.load_module_async('numpy', required=True)
        try:
            numpy_future.result(timeout=30)  # Give numpy time to load
        except Exception as e:
            self.logger.error(f"Failed to preload numpy: {e}")
            return
        
        # Load others in parallel
        for module in scientific_modules[1:]:
            self.load_module_async(module, required=False)


class ExecutionContext:
    """
    Manages execution context for widget threads including library initialization
    """
    
    def __init__(self, lazy_loading: bool = True):
        self.lazy_loading = lazy_loading
        self.is_initialized = False
        self.initialization_time = None
        
        # Lazy loader
        self.lazy_loader = LazyLoader()
        
        # Context data
        self.global_context: Dict[str, Any] = {}
        self.thread_contexts: Dict[int, Dict[str, Any]] = {}
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Thread safety
        self.context_lock = threading.Lock()
    
    def initialize(self):
        """Initialize the execution context"""
        start_time = time.time()
        
        try:
            self.logger.info("Initializing execution context...")
            
            # Set up global context
            self.global_context = {
                'initialized_at': start_time,
                'python_version': sys.version,
                'loaded_modules': set(),
                'config': {
                    'lazy_loading': self.lazy_loading,
                    'max_import_timeout': 30,
                    'preload_scientific': True
                }
            }
            
            if self.lazy_loading:
                # Start preloading scientific stack
                self.lazy_loader.preload_scientific_stack()
            else:
                # Load everything synchronously
                self._load_all_modules_sync()
            
            self.initialization_time = time.time() - start_time
            self.is_initialized = True
            
            self.logger.info(f"Execution context initialized in {self.initialization_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize execution context: {e}")
            raise
    
    def get_thread_context(self, thread_id: Optional[int] = None) -> Dict[str, Any]:
        """Get context for current or specified thread"""
        if thread_id is None:
            thread_id = threading.get_ident()
        
        with self.context_lock:
            if thread_id not in self.thread_contexts:
                self.thread_contexts[thread_id] = {
                    'thread_id': thread_id,
                    'created_at': time.time(),
                    'widget_executions': 0,
                    'loaded_modules': set(),
                    'imports': {}
                }
            
            return self.thread_contexts[thread_id]
    
    def prepare_widget_execution(self, widget_id: str, required_modules: Optional[List[str]] = None):
        """Prepare context for widget execution in current thread"""
        thread_context = self.get_thread_context()
        thread_context['widget_executions'] += 1
        
        # Load required modules for this widget
        if required_modules:
            if self.lazy_loading:
                # Load asynchronously
                for module in required_modules:
                    future = self.lazy_loader.load_module_async(module)
                    thread_context['imports'][module] = future
            else:
                # Load synchronously
                for module in required_modules:
                    try:
                        imported = importlib.import_module(module)
                        thread_context['imports'][module] = imported
                        thread_context['loaded_modules'].add(module)
                    except ImportError as e:
                        self.logger.warning(f"Could not load module {module} for widget {widget_id}: {e}")
    
    def wait_for_imports(self, thread_id: Optional[int] = None, timeout: float = 10.0) -> bool:
        """Wait for all pending imports in thread to complete"""
        thread_context = self.get_thread_context(thread_id)
        
        success = True
        for module, future_or_module in thread_context['imports'].items():
            if isinstance(future_or_module, Future):
                try:
                    result = future_or_module.result(timeout=timeout)
                    thread_context['imports'][module] = result  # Replace future with result
                    if result is not None:
                        thread_context['loaded_modules'].add(module)
                except Exception as e:
                    self.logger.error(f"Failed to load module {module}: {e}")
                    success = False
        
        return success
    
    def get_module(self, module_name: str, thread_id: Optional[int] = None):
        """Get a loaded module from thread context"""
        thread_context = self.get_thread_context(thread_id)
        
        # Check if already loaded
        if module_name in thread_context['imports']:
            module_or_future = thread_context['imports'][module_name]
            if isinstance(module_or_future, Future):
                # Wait for it to load
                try:
                    return module_or_future.result(timeout=5.0)
                except Exception:
                    return None
            else:
                return module_or_future
        
        # Try to load it now
        try:
            module = importlib.import_module(module_name)
            thread_context['imports'][module_name] = module
            thread_context['loaded_modules'].add(module_name)
            return module
        except ImportError:
            return None
    
    def _load_all_modules_sync(self):
        """Load all common modules synchronously"""
        common_modules = [
            'numpy',
            'matplotlib',
            'matplotlib.pyplot',
            'json',
            'datetime',
            'time',
            'os',
            'sys',
            'logging'
        ]
        
        loaded_count = 0
        for module in common_modules:
            try:
                importlib.import_module(module)
                self.global_context['loaded_modules'].add(module)
                loaded_count += 1
            except ImportError as e:
                self.logger.warning(f"Could not load module {module}: {e}")
        
        self.logger.info(f"Loaded {loaded_count}/{len(common_modules)} common modules")
    
    def cleanup(self):
        """Cleanup execution context"""
        self.logger.info("Cleaning up execution context")
        
        with self.context_lock:
            self.thread_contexts.clear()
        
        self.global_context.clear()
        self.is_initialized = False
        
        self.logger.info("Execution context cleanup complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
        with self.context_lock:
            return {
                'is_initialized': self.is_initialized,
                'initialization_time': self.initialization_time,
                'lazy_loading': self.lazy_loading,
                'global_modules_loaded': len(self.global_context.get('loaded_modules', set())),
                'active_threads': len(self.thread_contexts),
                'total_widget_executions': sum(ctx.get('widget_executions', 0) for ctx in self.thread_contexts.values()),
                'threads_with_loaded_modules': len([ctx for ctx in self.thread_contexts.values() if ctx.get('loaded_modules')])
            }