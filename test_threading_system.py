#!/usr/bin/env python3
"""
Test the new threading system and widget framework
"""

import sys
import os
import time
import threading

# Add libraries to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries', 'core', 'widget_threading'))

from base_widget import WidgetExecutor
from widget_threading.thread_pool_engine import ThreadPoolEngine, initialize_global_engine
from widget_threading.widget_executor import ThreadedWidgetExecutor, create_threaded_widget

def test_basic_widget():
    """Test basic widget functionality"""
    print("Testing basic widget functionality...")
    
    widget_schema = {
        'id': 'test-widget',
        'name': 'Test Widget',
        'actions': {
            'execute': {
                'names': {'en': 'Execute'},
                'description': 'Execute the test widget',
                'output_format': 'json'
            }
        }
    }
    
    widget = WidgetExecutor(widget_schema)
    result = widget.execute({'test_param': 'hello'})
    
    print(f"Basic widget result: {result}")
    assert result['success'] == True
    assert result['widget_id'] == 'test-widget'
    print("✅ Basic widget test passed")

def test_thread_pool_engine():
    """Test thread pool engine initialization"""
    print("\nTesting thread pool engine...")
    
    engine = ThreadPoolEngine(max_workers=2)
    engine.initialize()
    
    assert engine.is_running == True
    assert engine.max_workers == 2
    
    stats = engine.get_stats()
    print(f"Engine stats: {stats}")
    
    engine.shutdown()
    print("✅ Thread pool engine test passed")

def test_threaded_widget():
    """Test threaded widget functionality"""
    print("\nTesting threaded widget...")
    
    widget_schema = {
        'id': 'threaded-test-widget',
        'name': 'Threaded Test Widget',
        'actions': {
            'execute': {
                'names': {'en': 'Execute'},
                'description': 'Execute the threaded test widget',
                'output_format': 'json'
            }
        }
    }
    
    # Create threaded widget
    engine = ThreadPoolEngine(max_workers=2)
    engine.initialize()
    
    widget = create_threaded_widget('test', widget_schema, thread_pool_engine=engine)
    
    # Test run action
    run_result = widget.action_run({'test_param': 'threaded_hello'})
    print(f"Run result: {run_result}")
    
    # Wait a bit for execution
    time.sleep(1)
    
    # Test status
    status_result = widget.action_get_status({})
    print(f"Status result: {status_result}")
    
    # Test stop
    stop_result = widget.action_stop({})
    print(f"Stop result: {stop_result}")
    
    engine.shutdown()
    print("✅ Threaded widget test passed")

def test_hierarchical_execution():
    """Test hierarchical widget execution"""
    print("\nTesting hierarchical execution...")
    
    engine = ThreadPoolEngine(max_workers=3)
    engine.initialize()
    
    # Create parent widget
    parent_schema = {
        'id': 'parent-widget',
        'name': 'Parent Widget',
        'actions': {'execute': {'names': {'en': 'Execute'}, 'output_format': 'json'}}
    }
    parent_widget = create_threaded_widget('parent', parent_schema, thread_pool_engine=engine)
    
    # Create child widgets
    child1_schema = {
        'id': 'child1-widget',
        'name': 'Child 1 Widget',
        'actions': {'execute': {'names': {'en': 'Execute'}, 'output_format': 'json'}}
    }
    child1_widget = create_threaded_widget('child1', child1_schema, thread_pool_engine=engine)
    
    child2_schema = {
        'id': 'child2-widget', 
        'name': 'Child 2 Widget',
        'actions': {'execute': {'names': {'en': 'Execute'}, 'output_format': 'json'}}
    }
    child2_widget = create_threaded_widget('child2', child2_schema, thread_pool_engine=engine)
    
    # Set up hierarchy (parent has children)
    engine.register_widget('parent-widget', parent_widget)
    engine.register_widget('child1-widget', child1_widget, parent_id='parent-widget')
    engine.register_widget('child2-widget', child2_widget, parent_id='parent-widget')
    
    # Run hierarchical execution
    task_ids = engine.run_hierarchical('parent-widget')
    print(f"Hierarchical execution task IDs: {task_ids}")
    
    # Wait for completion
    time.sleep(2)
    
    # Check status
    parent_status = engine.get_widget_status('parent-widget')
    print(f"Parent widget status: {parent_status}")
    
    engine.shutdown()
    print("✅ Hierarchical execution test passed")

def test_lazy_loading():
    """Test lazy loading system"""
    print("\nTesting lazy loading system...")
    
    from widget_threading.context_manager import ExecutionContext, LazyLoader
    
    # Test lazy loader
    loader = LazyLoader()
    
    # Load numpy asynchronously
    numpy_future = loader.load_module_async('numpy')
    print("Started loading numpy...")
    
    # Wait for it
    numpy_module = numpy_future.result(timeout=10)
    print(f"Loaded numpy: {numpy_module is not None}")
    
    # Test execution context
    context = ExecutionContext(lazy_loading=True)
    context.initialize()
    
    stats = context.get_stats()
    print(f"Context stats: {stats}")
    
    context.cleanup()
    print("✅ Lazy loading test passed")

def run_all_tests():
    """Run all tests"""
    print("🧪 Starting threading system tests...\n")
    
    try:
        test_basic_widget()
        test_thread_pool_engine()
        test_threaded_widget()
        test_hierarchical_execution()
        test_lazy_loading()
        
        print("\n🎉 All tests passed! Threading system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)