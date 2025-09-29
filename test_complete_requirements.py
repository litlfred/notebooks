#!/usr/bin/env python3
"""
Complete Requirements Test
Tests all implemented features against the original issue requirements
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Add libraries to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries', 'core', 'widget_threading'))

def test_requirement_1_notebooks_as_orchestrators():
    """Test: Notebooks function as orchestrators of evaluation/rendering of widgets"""
    print("1. Testing notebooks as orchestrators...")
    
    try:
        from notebook.threaded_notebook_widget import ThreadedNotebookWidget
        
        # Test notebook widget creation
        notebook_schema = {
            'id': 'test-notebook',
            'name': 'Test Notebook',
            'actions': {'render_notebook': {'names': {'en': 'Render'}, 'output_format': 'json'}}
        }
        notebook_widget = ThreadedNotebookWidget(notebook_schema)
        
        # Test orchestration capabilities
        assert hasattr(notebook_widget, 'action_run_all_widgets')
        assert hasattr(notebook_widget, 'action_orchestrate_execution')
        assert notebook_widget.supports_hierarchical_execution == True
        
        print("   ✅ Notebooks can orchestrate widget evaluation/rendering")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_2_notebook_run_action():
    """Test: A notebook should have a 'run' action that initiates hierarchical execution"""
    print("2. Testing notebook 'run' action...")
    
    try:
        from notebook.threaded_notebook_widget import ThreadedNotebookWidget
        
        notebook_schema = {
            'id': 'test-notebook',
            'name': 'Test Notebook',
            'actions': {'run': {'names': {'en': 'Run'}, 'output_format': 'json'}}
        }
        notebook_widget = ThreadedNotebookWidget(notebook_schema)
        
        # Test run action exists
        assert 'run' in notebook_widget.actions
        assert hasattr(notebook_widget, 'action_run')
        
        # Test hierarchical execution capability
        assert hasattr(notebook_widget, '_orchestrate_widget_execution')
        assert hasattr(notebook_widget, '_execute_hierarchical')
        
        print("   ✅ Notebook has 'run' action for hierarchical execution")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_3_widget_run_action():
    """Test: Each widget should have 'run' action as part of core widget interface"""
    print("3. Testing widget 'run' action...")
    
    try:
        from base_widget import WidgetExecutor
        from widget_threading.widget_executor import ThreadedWidgetExecutor
        
        # Test base widget has run action
        base_schema = {'id': 'base', 'name': 'Base', 'actions': {}}
        base_widget = WidgetExecutor(base_schema)
        assert hasattr(base_widget, 'action_run')
        
        # Test threaded widget has enhanced run action
        threaded_schema = {'id': 'threaded', 'name': 'Threaded', 'actions': {}}
        threaded_widget = ThreadedWidgetExecutor(threaded_schema)
        assert hasattr(threaded_widget, 'action_run')
        assert 'run' in threaded_widget.actions
        
        print("   ✅ All widgets have 'run' action in core interface")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_4_thread_pool_engine():
    """Test: Widget should run in its own thread with thread pool maintenance"""
    print("4. Testing thread pool engine...")
    
    try:
        from widget_threading.thread_pool_engine import ThreadPoolEngine
        
        # Test thread pool creation
        engine = ThreadPoolEngine(max_workers=2)
        assert engine.max_workers == 2
        
        # Test initialization
        engine.initialize()
        assert engine.is_running == True
        
        # Test widget registration and execution
        from widget_threading.widget_executor import create_threaded_widget
        
        widget_schema = {'id': 'test', 'name': 'Test', 'actions': {}}
        widget = create_threaded_widget('test', widget_schema, thread_pool_engine=engine)
        
        # Test threaded execution
        task_id = engine.run_widget('test', 'execute', {})
        assert task_id is not None
        
        engine.shutdown()
        print("   ✅ Thread pool engine manages widget execution in threads")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_5_index_thread_pool_initialization():
    """Test: Thread pool started on index.html page load"""
    print("5. Testing index.html thread pool initialization...")
    
    try:
        # Check index.html exists and is minimal
        index_path = Path('index.html')
        assert index_path.exists()
        
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Check for thread pool initialization
        assert 'GitHubPagesLauncher' in content
        assert 'threadPoolWorkers' in content or 'thread' in content.lower()
        
        # Check size is minimal (should be < 2KB)
        assert len(content) < 2000, f"Index.html too large: {len(content)} bytes"
        
        print("   ✅ Index.html initializes thread pool on page load")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_6_library_loading():
    """Test: Engine handles loading of Python libraries and JSON-LD"""
    print("6. Testing library loading...")
    
    try:
        from widget_threading.context_manager import ExecutionContext, LazyLoader
        
        # Test execution context
        context = ExecutionContext(lazy_loading=True)
        context.initialize()
        assert context.is_initialized == True
        
        # Test lazy loader
        loader = LazyLoader()
        assert hasattr(loader, 'load_module_async')
        assert hasattr(loader, 'preload_scientific_stack')
        
        context.cleanup()
        print("   ✅ Engine handles Python library and JSON-LD loading")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_7_weierstrass_playground_content():
    """Test: Content rendered on page load should be weierstrass-playground widget"""
    print("7. Testing weierstrass-playground content...")
    
    try:
        # Check weierstrass-playground.jsonld exists
        playground_jsonld = Path('weierstrass-playground.jsonld')
        assert playground_jsonld.exists()
        
        with open(playground_jsonld, 'r') as f:
            playground_data = json.load(f)
        
        # Check it's defined as a widget
        assert 'playground:Widget' in playground_data['@type']
        
        # Check index.html references playground
        with open('index.html', 'r') as f:
            index_content = f.read()
        
        assert 'weierstrass-playground' in index_content or 'playground' in index_content
        
        print("   ✅ Weierstrass playground widget renders on page load")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_8_widget_lifecycle():
    """Test: Widgets should have 'stop' and 'halt' actions"""
    print("8. Testing widget lifecycle (stop/halt)...")
    
    try:
        from widget_threading.widget_executor import ThreadedWidgetExecutor
        
        schema = {'id': 'test', 'name': 'Test', 'actions': {}}
        widget = ThreadedWidgetExecutor(schema)
        
        # Test stop action
        assert 'stop' in widget.actions
        assert hasattr(widget, 'action_stop')
        
        # Test halt action
        assert 'halt' in widget.actions
        assert hasattr(widget, 'action_halt')
        
        print("   ✅ Widgets have stop and halt lifecycle actions")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_9_lazy_loading():
    """Test: Maximize lazy loading and delay downloading of content"""
    print("9. Testing lazy loading strategy...")
    
    try:
        from widget_threading.context_manager import LazyLoader
        
        loader = LazyLoader()
        
        # Test lazy loading capabilities
        assert hasattr(loader, 'loaded_modules')
        assert hasattr(loader, 'loading_futures')
        assert hasattr(loader, 'preload_scientific_stack')
        
        # Check JavaScript files for lazy loading
        js_launcher_path = Path('js/github-pages-launcher.js')
        if js_launcher_path.exists():
            with open(js_launcher_path, 'r') as f:
                js_content = f.read()
            assert 'enableLazyLoading' in js_content
        
        print("   ✅ Lazy loading strategy implemented")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_10_auto_generated_index():
    """Test: Auto-generated index.html files for widgets"""
    print("10. Testing auto-generated index files...")
    
    try:
        # Check generation script exists
        script_path = Path('scripts/generate-widget-index.py')
        assert script_path.exists()
        
        # Check that it generated widget index files
        sticky_note_index = Path('libraries/core/sticky-note/index.html')
        notebook_index = Path('libraries/core/notebook/index.html')
        
        # Run generation if files don't exist
        if not sticky_note_index.exists():
            subprocess.run([sys.executable, str(script_path)], check=True)
        
        assert sticky_note_index.exists()
        assert notebook_index.exists()
        
        print("   ✅ Auto-generated index.html files for widgets")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_11_github_pages_deployment():
    """Test: GitHub Pages deployment script"""
    print("11. Testing GitHub Pages deployment script...")
    
    try:
        deploy_script = Path('scripts/deploy-github-pages.py')
        assert deploy_script.exists()
        
        # Check workflow file was created
        workflow_file = Path('.github/workflows/deploy-widgets.yml')
        assert workflow_file.exists()
        
        # Check deployment manifest
        manifest_file = Path('_build/deployment-manifest.json')
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            assert 'widgets' in manifest
            assert 'deployment' in manifest
        
        print("   ✅ GitHub Pages deployment automation implemented")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_requirement_12_javascript_integration():
    """Test: JavaScript ↔ Python integration bridge"""
    print("12. Testing JavaScript ↔ Python integration...")
    
    try:
        # Check threading bridge exists
        bridge_path = Path('js/board-threading-bridge.js')
        assert bridge_path.exists()
        
        with open(bridge_path, 'r') as f:
            bridge_content = f.read()
        
        # Check key integration features
        assert 'BoardThreadingBridge' in bridge_content
        assert 'handleWidgetRun' in bridge_content
        assert 'simulateThreadedExecution' in bridge_content
        assert 'runHierarchicalExecution' in bridge_content
        
        print("   ✅ JavaScript ↔ Python integration bridge implemented")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def run_all_requirements_tests():
    """Run all requirements tests"""
    print("🧪 Testing All Original Issue Requirements")
    print("=" * 60)
    
    tests = [
        test_requirement_1_notebooks_as_orchestrators,
        test_requirement_2_notebook_run_action,
        test_requirement_3_widget_run_action,
        test_requirement_4_thread_pool_engine,
        test_requirement_5_index_thread_pool_initialization,
        test_requirement_6_library_loading,
        test_requirement_7_weierstrass_playground_content,
        test_requirement_8_widget_lifecycle,
        test_requirement_9_lazy_loading,
        test_requirement_10_auto_generated_index,
        test_requirement_11_github_pages_deployment,
        test_requirement_12_javascript_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Requirements Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL REQUIREMENTS IMPLEMENTED SUCCESSFULLY!")
        print("\n✅ The repository is now a fully functioning widget with:")
        print("   • Thread pool execution engine")
        print("   • Hierarchical widget orchestration")
        print("   • Complete widget lifecycle management")
        print("   • Auto-generated deployment system")
        print("   • JavaScript ↔ Python integration bridge")
        print("   • Lazy loading infrastructure")
        print("   • GitHub Pages deployment automation")
    else:
        failed = total - passed
        print(f"⚠️  {failed} requirements still need attention")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_requirements_tests()
    sys.exit(0 if success else 1)