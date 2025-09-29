#!/usr/bin/env python3
"""
GitHub Pages Deployment Script
Automates index.html generation and deployment preparation
"""

import sys
import os
import json  
import shutil
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# Import WidgetIndexGenerator by executing the module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Execute the generate-widget-index script to get the class
generate_script = os.path.join(script_dir, 'generate-widget-index.py')
with open(generate_script, 'r') as f:
    generate_code = f.read()

# Create a namespace to execute the code
generate_namespace = {}
exec(generate_code, generate_namespace)
WidgetIndexGenerator = generate_namespace['WidgetIndexGenerator']

class GitHubPagesDeployer:
    """Deploy widgets to GitHub Pages with automated index generation"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.build_dir = self.repo_root / "_build"
        self.docs_dir = self.repo_root / "docs"
        
    def prepare_deployment(self):
        """Prepare deployment by generating all necessary files"""
        print("🚀 GitHub Pages Deployment Preparation")
        print("=" * 50)
        
        # Clean build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir()
        
        # Generate widget index files
        print("\n📝 Generating widget index files...")
        generator = WidgetIndexGenerator(str(self.repo_root))
        generated_files = generator.generate_all_widget_indexes()
        
        # Copy core files to docs if needed
        self.ensure_docs_structure()
        
        # Generate deployment manifest
        manifest = self.create_deployment_manifest(generated_files)
        self.write_deployment_manifest(manifest)
        
        # Validate deployment
        self.validate_deployment()
        
        print("\n✅ Deployment preparation complete!")
        return manifest
    
    def ensure_docs_structure(self):
        """Ensure docs directory has proper structure for GitHub Pages"""
        print("\n📁 Ensuring docs structure...")
        
        # Copy JavaScript files to docs if they don't exist
        docs_js_dir = self.docs_dir / "js"
        repo_js_dir = self.repo_root / "js"
        
        if repo_js_dir.exists() and not docs_js_dir.exists():
            shutil.copytree(repo_js_dir, docs_js_dir)
            print(f"  ✓ Copied JS files to {docs_js_dir}")
        
        # Copy root index.html to docs if needed
        docs_index = self.docs_dir / "index.html"
        repo_index = self.repo_root / "index.html"
        
        if repo_index.exists() and not docs_index.exists():
            shutil.copy2(repo_index, docs_index)
            print(f"  ✓ Copied index.html to docs/")
    
    def create_deployment_manifest(self, generated_files: List[str]) -> Dict[str, Any]:
        """Create deployment manifest"""
        # Discover all widgets
        generator = WidgetIndexGenerator(str(self.repo_root))
        widgets = generator.discover_widgets()
        
        manifest = {
            "deployment": {
                "timestamp": self.get_timestamp(),
                "generator_version": "1.0.0",
                "repository": "litlfred/notebooks",
                "github_pages_url": "https://litlfred.github.io/notebooks"
            },
            "widgets": {
                "total_count": len(widgets),
                "by_type": self.group_widgets_by_type(widgets),
                "by_library": self.group_widgets_by_library(widgets)
            },
            "generated_files": {
                "index_files": generated_files,
                "total_generated": len(generated_files)
            },
            "routes": self.create_widget_routes(widgets),
            "assets": {
                "javascript": ["js/github-pages-launcher.js"],
                "css": ["js/minimal-launcher-styles.css"],
                "python": ["libraries/core/widget_threading/", "libraries/core/widget_integration.py"]
            }
        }
        
        return manifest
    
    def group_widgets_by_type(self, widgets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group widgets by type for statistics"""
        type_counts = {}
        for widget in widgets:
            widget_type = widget['type']
            type_counts[widget_type] = type_counts.get(widget_type, 0) + 1
        return type_counts
    
    def group_widgets_by_library(self, widgets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group widgets by library for statistics"""
        library_counts = {}
        for widget in widgets:
            library = widget['library']
            library_counts[library] = library_counts.get(library, 0) + 1
        return library_counts
    
    def create_widget_routes(self, widgets: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create routing information for widgets"""
        routes = {}
        
        for widget in widgets:
            if widget['library'] == 'root':
                routes[widget['id']] = "/"
            else:
                routes[widget['id']] = f"/libraries/{widget['library']}/{widget['id']}/"
        
        return routes
    
    def write_deployment_manifest(self, manifest: Dict[str, Any]):
        """Write deployment manifest to file"""
        manifest_file = self.build_dir / "deployment-manifest.json"
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  ✓ Created deployment manifest: {manifest_file}")
        
        # Also write to docs for GitHub Pages access
        docs_manifest = self.docs_dir / "deployment-manifest.json"
        with open(docs_manifest, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  ✓ Created docs manifest: {docs_manifest}")
    
    def validate_deployment(self):
        """Validate that deployment is ready"""
        print("\n🔍 Validating deployment...")
        
        issues = []
        
        # Check that index.html exists
        if not (self.repo_root / "index.html").exists():
            issues.append("Missing root index.html")
        
        # Check that JS files exist
        js_dir = self.repo_root / "js"
        if not js_dir.exists():
            issues.append("Missing js/ directory")
        else:
            required_js = ["github-pages-launcher.js", "minimal-launcher-styles.css"]
            for js_file in required_js:
                if not (js_dir / js_file).exists():
                    issues.append(f"Missing js/{js_file}")
        
        # Check that core libraries exist
        core_lib_dir = self.repo_root / "libraries" / "core"
        if not core_lib_dir.exists():
            issues.append("Missing libraries/core/")
        
        # Check weierstrass playground
        playground_dir = self.repo_root / "docs" / "weierstrass-playground"
        if not playground_dir.exists():
            issues.append("Missing docs/weierstrass-playground/")
        
        if issues:
            print("  ⚠️ Validation issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ Deployment validation passed!")
        
        return len(issues) == 0
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_github_workflow(self):
        """Create GitHub Actions workflow for automated deployment"""
        workflow_dir = self.repo_root / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / "deploy-widgets.yml"
        
        workflow_content = """name: Deploy Widgets to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Generate widget index files
      run: |
        python scripts/generate-widget-index.py
    
    - name: Prepare GitHub Pages deployment
      run: |
        python scripts/deploy-github-pages.py
    
    - name: Setup Pages
      uses: actions/configure-pages@v4
    
    - name: Build with Jekyll
      uses: actions/jekyll-build-pages@v1
      with:
        source: ./docs
        destination: ./_site
    
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v3
"""
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"  ✓ Created GitHub Actions workflow: {workflow_file}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        repo_root = os.getcwd()
    else:
        repo_root = sys.argv[1]
    
    deployer = GitHubPagesDeployer(repo_root)
    
    # Prepare deployment
    manifest = deployer.prepare_deployment()
    
    # Create GitHub workflow
    deployer.create_github_workflow()
    
    print("\n🎉 GitHub Pages deployment preparation complete!")
    print(f"📊 Generated {manifest['generated_files']['total_generated']} widget index files")
    print(f"🔗 {manifest['widgets']['total_count']} widgets ready for deployment")
    print("\nNext steps:")
    print("1. Commit the generated files")
    print("2. Push to GitHub")
    print("3. GitHub Actions will automatically deploy to Pages")

if __name__ == "__main__":
    main()