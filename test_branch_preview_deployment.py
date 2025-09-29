#!/usr/bin/env python3
"""
Test URL Service and Branch Preview Deployment System
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, 'scripts')
sys.path.insert(0, scripts_dir)

from url_service import URLService


def test_url_service_preview_deployment():
    """Test URL service for preview deployment"""
    print("🧪 Testing URL service for preview deployment...")
    
    # Set environment variables for preview
    os.environ['DEPLOYMENT_TYPE'] = 'preview'
    os.environ['GITHUB_REF_NAME'] = 'feature-awesome-widget'
    os.environ['GITHUB_REPOSITORY'] = 'litlfred/notebooks'
    
    service = URLService()
    
    # Test base URL generation
    expected_base = "https://litlfred.github.io/notebooks/branch-preview/feature-awesome-widget"
    assert service.get_base_url() == expected_base, f"Expected {expected_base}, got {service.get_base_url()}"
    
    # Test schema URL generation
    schema_url = service.get_schema_url("schema/libraries/core/input.schema.json")
    expected_schema = f"{expected_base}/schema/libraries/core/input.schema.json"
    assert schema_url == expected_schema, f"Expected {expected_schema}, got {schema_url}"
    
    # Test library URL generation
    library_url = service.get_library_url("pq-torus", "widget.schema.json")
    expected_library = f"{expected_base}/libraries/pq-torus/widget.schema.json"
    assert library_url == expected_library, f"Expected {expected_library}, got {library_url}"
    
    print("  ✅ Preview deployment URLs generated correctly")


def test_url_service_production_deployment():
    """Test URL service for production deployment"""
    print("🧪 Testing URL service for production deployment...")
    
    # Set environment variables for production
    os.environ['DEPLOYMENT_TYPE'] = 'production'
    os.environ['GITHUB_REF_NAME'] = 'main'
    os.environ['GITHUB_REPOSITORY'] = 'litlfred/notebooks'
    
    service = URLService()
    
    # Test base URL generation
    expected_base = "https://litlfred.github.io/notebooks"
    assert service.get_base_url() == expected_base, f"Expected {expected_base}, got {service.get_base_url()}"
    
    # Test schema URL generation
    schema_url = service.get_schema_url("schema/libraries/core/input.schema.json")
    expected_schema = f"{expected_base}/schema/libraries/core/input.schema.json"
    assert schema_url == expected_schema, f"Expected {expected_schema}, got {schema_url}"
    
    # Test deployment info
    info = service.get_deployment_info()
    assert info['deployment_type'] == 'production'
    assert info['branch'] == 'main'
    assert info['base_url'] == expected_base
    
    print("  ✅ Production deployment URLs generated correctly")


def test_branch_name_sanitization():
    """Test branch name sanitization for URLs"""
    print("🧪 Testing branch name sanitization...")
    
    test_cases = [
        ("feature/awesome-widget", "feature-awesome-widget"),
        ("fix#123-bug", "fix-123-bug"),
        ("user@domain.com/fix", "user-domain-com-fix"),
        ("feature--double--dash", "feature-double-dash"),
        ("-leading-and-trailing-", "leading-and-trailing"),
    ]
    
    # Set deployment type to preview for all tests
    os.environ['DEPLOYMENT_TYPE'] = 'preview'
    os.environ['GITHUB_REPOSITORY'] = 'litlfred/notebooks'
    
    for input_branch, expected_output in test_cases:
        os.environ['GITHUB_REF_NAME'] = input_branch
        service = URLService()
        
        # Extract sanitized branch from base URL
        base_url = service.get_base_url()
        if '/branch-preview/' in base_url:
            sanitized = base_url.split('/branch-preview/')[-1]
        else:
            # Fallback: test sanitization method directly
            sanitized = service._sanitize_branch_name(input_branch)
        
        assert sanitized == expected_output, f"Input: {input_branch}, Expected: {expected_output}, Got: {sanitized}"
    
    print("  ✅ Branch name sanitization working correctly")


def test_url_config_generation():
    """Test URL configuration generation for frontend"""
    print("🧪 Testing URL configuration generation...")
    
    # Test preview deployment config
    os.environ['DEPLOYMENT_TYPE'] = 'preview'
    os.environ['GITHUB_REF_NAME'] = 'feature-test'
    
    service = URLService()
    config = service.generate_url_config()
    
    # Verify config structure
    required_keys = ['baseUrl', 'deploymentType', 'repository', 'branch', 'urls']
    for key in required_keys:
        assert key in config, f"Missing required key: {key}"
    
    # Verify URLs structure
    url_keys = ['schemas', 'libraries', 'widgets', 'notebooks']
    for key in url_keys:
        assert key in config['urls'], f"Missing URL key: {key}"
        assert config['urls'][key].startswith(config['baseUrl']), f"URL {key} doesn't start with base URL"
    
    print("  ✅ URL configuration generation working correctly")


def test_url_update_functionality():
    """Test URL update functionality"""
    print("🧪 Testing URL update functionality...")
    
    # Create a temporary file with hardcoded URLs
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_content = {
            "$id": "https://litlfred.github.io/notebooks/schema/test.json",
            "properties": {
                "reference": "https://litlfred.github.io/notebooks/libraries/core/"
            }
        }
        json.dump(test_content, f, indent=2)
        temp_file = f.name
    
    try:
        # Test URL update
        os.environ['DEPLOYMENT_TYPE'] = 'preview'
        os.environ['GITHUB_REF_NAME'] = 'feature-test'
        
        service = URLService()
        
        # Read and update content
        with open(temp_file, 'r') as f:
            content = f.read()
        
        updated_content = service.update_schema_urls(content)
        
        # Verify URLs were updated
        expected_base = "https://litlfred.github.io/notebooks/branch-preview/feature-test"
        assert expected_base in updated_content, "URLs were not updated correctly"
        assert "branch-preview/feature-test" in updated_content, "Preview branch path not found"
        
        print("  ✅ URL update functionality working correctly")
    
    finally:
        # Clean up
        os.unlink(temp_file)


def test_environment_variable_handling():
    """Test handling of environment variables"""
    print("🧪 Testing environment variable handling...")
    
    # Test with minimal environment
    for key in ['DEPLOYMENT_TYPE', 'GITHUB_REF_NAME', 'GITHUB_REPOSITORY']:
        if key in os.environ:
            del os.environ[key]
    
    service = URLService()
    
    # Should fall back to defaults
    info = service.get_deployment_info()
    assert info['deployment_type'] == 'preview'  # Default
    assert info['repository'] == 'litlfred/notebooks'  # Default
    assert info['branch'] == 'main'  # Default
    
    print("  ✅ Environment variable handling working correctly")


def run_all_tests():
    """Run all tests"""
    print("🧪 Running URL Service and Branch Preview Tests")
    print("=" * 60)
    
    tests = [
        test_url_service_preview_deployment,
        test_url_service_production_deployment,
        test_branch_name_sanitization,
        test_url_config_generation,
        test_url_update_functionality,
        test_environment_variable_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n📊 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📈 Success rate: {passed}/{len(tests)} ({100*passed//len(tests)}%)")
    
    if failed == 0:
        print("\n🎉 All tests passed! Branch preview deployment system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)