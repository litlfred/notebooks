#!/usr/bin/env python3
"""
Branch Preview Deployment System Demo
Demonstrates the new preview deployment capabilities
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, 'scripts')
sys.path.insert(0, scripts_dir)

from url_service import URLService


def demo_preview_deployment():
    """Demonstrate preview deployment URL generation"""
    print("🔀 Branch Preview Deployment Demo")
    print("=" * 50)
    
    # Demo various branch scenarios
    scenarios = [
        ("feature-awesome-widget", "Feature development"),
        ("fix/critical-bug", "Bug fix branch"),
        ("user@domain/feature", "User branch with special chars"),
        ("release-v2.0", "Release branch"),
        ("main", "Main branch preview"),
    ]
    
    for branch, description in scenarios:
        print(f"\n📌 Scenario: {description}")
        print(f"   Branch: {branch}")
        
        # Set environment for preview
        os.environ['DEPLOYMENT_TYPE'] = 'preview'
        os.environ['GITHUB_REF_NAME'] = branch
        os.environ['GITHUB_REPOSITORY'] = 'litlfred/notebooks'
        
        service = URLService()
        base_url = service.get_base_url()
        
        print(f"   Preview URL: {base_url}")
        print(f"   Schema URL: {service.get_schema_url('schema/libraries/core/input.schema.json')}")
        print(f"   Widget URL: {service.get_widget_url('weierstrass-playground')}")


def demo_production_deployment():
    """Demonstrate production deployment URL generation"""
    print("\n🚀 Production Deployment Demo")
    print("=" * 50)
    
    # Set environment for production
    os.environ['DEPLOYMENT_TYPE'] = 'production'
    os.environ['GITHUB_REF_NAME'] = 'main'
    os.environ['GITHUB_REPOSITORY'] = 'litlfred/notebooks'
    
    service = URLService()
    base_url = service.get_base_url()
    
    print(f"Production URL: {base_url}")
    print(f"Schema URL: {service.get_schema_url('schema/libraries/core/input.schema.json')}")
    print(f"Widget URL: {service.get_widget_url('weierstrass-playground')}")
    print(f"Library URL: {service.get_library_url('pq-torus', 'widget.schema.json')}")


def demo_deployment_workflow():
    """Demonstrate deployment workflow usage"""
    print("\n⚙️ Deployment Workflow Demo")
    print("=" * 50)
    
    print("1️⃣ Feature Branch Preview:")
    print("   • Push to any feature branch")
    print("   • OR use workflow dispatch: .github/workflows/branch-preview-deploy.yml")
    print("   • Deploys to: litlfred.github.io/notebooks/branch-preview/{branch-name}")
    print("")
    
    print("2️⃣ Main Branch Preview:")
    print("   • Push to main branch")
    print("   • Deploys to: litlfred.github.io/notebooks/branch-preview/main")
    print("")
    
    print("3️⃣ Production Deployment:")
    print("   • Use workflow dispatch: .github/workflows/deploy.yml")
    print("   • Set deployment_type: 'production'")
    print("   • Deploys to: litlfred.github.io/notebooks (root)")
    print("")
    
    print("🔧 Available Workflows:")
    workflows_dir = Path('.github/workflows')
    if workflows_dir.exists():
        for workflow in workflows_dir.glob('*.yml'):
            if 'deploy' in workflow.name or 'preview' in workflow.name:
                print(f"   • {workflow.name}")


def demo_url_service_integration():
    """Demonstrate URL service integration"""
    print("\n🌐 URL Service Integration Demo")
    print("=" * 50)
    
    # Show JavaScript integration
    js_service_path = Path('docs/js/url-service.js')
    if js_service_path.exists():
        print("✅ JavaScript URL Service Available:")
        print(f"   📁 Location: {js_service_path}")
        print("   🔧 Usage: window.urlService.getBaseUrl()")
        print("   🎯 Features: Auto-detection of deployment context")
    
    print("")
    
    # Show Python integration
    print("✅ Python URL Service Available:")
    print("   📁 Location: scripts/url_service.py")
    print("   🔧 Usage: from scripts.url_service import URLService")
    print("   🎯 Features: Environment-aware URL generation")
    
    print("")
    
    # Show deployment configuration
    config_path = Path('docs/deployment-config.json')
    if config_path.exists():
        print("✅ Deployment Configuration Generated:")
        print(f"   📁 Location: {config_path}")
        print("   🔧 Usage: fetch('./deployment-config.json')")
        print("   🎯 Features: Runtime deployment detection")


def main():
    """Run the complete demo"""
    print("🎯 Branch Preview Deployment System")
    print("litlfred/notebooks repository")
    print("Created as part of issue implementation")
    print("")
    
    # Run all demos
    demo_preview_deployment()
    demo_production_deployment()
    demo_deployment_workflow()
    demo_url_service_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("")
    print("📚 Next Steps:")
    print("1. Test the workflows using GitHub UI workflow dispatch")
    print("2. Deploy a feature branch using branch-preview-deploy.yml")
    print("3. Deploy to production using deploy.yml with production mode")
    print("4. Verify URLs are working correctly in deployed environments")
    print("")
    print("💡 All URLs are now environment-aware and will automatically")
    print("   adjust between preview and production deployments!")


if __name__ == "__main__":
    main()