#!/usr/bin/env python3
"""
Preview Branch Deployment Script
Handles deployment of feature branches to GitHub Pages preview locations
"""

import sys
import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class PreviewBranchDeployer:
    """Deploy feature branches to preview locations on GitHub Pages"""
    
    def __init__(self, repo_root: str, branch_name: str, repo_owner: str = "litlfred", repo_name: str = "notebooks"):
        self.repo_root = Path(repo_root)
        self.branch_name = branch_name
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        # Determine deployment context
        self.is_production = branch_name == "main" and os.getenv("DEPLOYMENT_TYPE") == "production"
        self.is_preview = not self.is_production
        
        # Set up URLs based on deployment type
        if self.is_production:
            self.base_url = f"https://{repo_owner}.github.io/{repo_name}"
            self.deployment_path = ""
        else:
            self.base_url = f"https://{repo_owner}.github.io/{repo_name}/branch-preview/{branch_name}"
            self.deployment_path = f"branch-preview/{branch_name}"
        
        # Schema URLs always point to production for consistency
        self.schema_base_url = f"https://{repo_owner}.github.io/{repo_name}"
        
        print(f"🚀 Preview Branch Deployer initialized:")
        print(f"   Branch: {branch_name}")
        print(f"   Deployment Type: {'Production' if self.is_production else 'Preview'}")
        print(f"   Base URL: {self.base_url}")
        print(f"   Schema Base URL: {self.schema_base_url}")

    def prepare_preview_deployment(self) -> Dict[str, Any]:
        """Prepare deployment with environment-specific configurations"""
        print("\n📦 Preparing preview deployment...")
        
        # Create deployment directory
        deploy_dir = self.repo_root / "_deploy"
        if deploy_dir.exists():
            shutil.rmtree(deploy_dir)
        deploy_dir.mkdir()
        
        # Copy docs directory to deployment location
        docs_source = self.repo_root / "docs"
        if self.deployment_path:
            # Preview deployment - create subdirectory structure
            preview_dir = deploy_dir / "branch-preview" / self.branch_name
            preview_dir.mkdir(parents=True)
            
            # Copy docs contents to preview directory
            shutil.copytree(docs_source, preview_dir, dirs_exist_ok=True)
            
            # Create root index.html that redirects to preview
            self.create_preview_index(deploy_dir)
        else:
            # Production deployment - copy directly
            shutil.copytree(docs_source, deploy_dir, dirs_exist_ok=True)
        
        # Update URLs in deployed files
        self.update_deployment_urls(deploy_dir)
        
        # Create deployment manifest
        manifest = self.create_deployment_manifest()
        self.write_deployment_manifest(deploy_dir, manifest)
        
        print(f"✅ Preview deployment prepared at: {deploy_dir}")
        return manifest

    def create_preview_index(self, deploy_dir: Path):
        """Create a root index.html for preview deployments"""
        index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Branch Preview - {self.branch_name}</title>
    <meta http-equiv="refresh" content="0;url=./{self.deployment_path}/">
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            text-align: center;
            max-width: 600px;
        }}
        .branch-badge {{
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        a {{
            color: #FFD700;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="branch-badge">Preview Branch</div>
        <h1>Notebooks - {self.branch_name}</h1>
        <p>Redirecting to branch preview...</p>
        <p>If you are not redirected automatically, <a href="./{self.deployment_path}/">click here</a>.</p>
        
        <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
            <p>📦 Repository: {self.repo_owner}/{self.repo_name}</p>
            <p>🌿 Branch: {self.branch_name}</p>
            <p>🔗 Preview URL: <a href="{self.base_url}">{self.base_url}</a></p>
        </div>
    </div>
</body>
</html>"""
        
        index_file = deploy_dir / "index.html"
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"  ✓ Created preview index: {index_file}")

    def update_deployment_urls(self, deploy_dir: Path):
        """Update URLs in deployment files to be environment-aware"""
        print("🔧 Updating URLs for deployment environment...")
        
        # Find all JavaScript and JSON files that might contain URLs
        for pattern in ["**/*.js", "**/*.json", "**/*.jsonld", "**/*.html"]:
            for file_path in deploy_dir.glob(pattern):
                if file_path.is_file():
                    self.update_file_urls(file_path)

    def update_file_urls(self, file_path: Path):
        """Update URLs in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if no URLs to update
            if 'litlfred.github.io' not in content:
                return
            
            original_content = content
            
            # Update hardcoded GitHub Pages URLs to be environment-aware
            # But keep schema URLs pointing to production
            
            # Replace URLs in JavaScript files with environment-aware versions
            if file_path.suffix == '.js':
                # Update resource URLs but keep schema URLs absolute
                content = content.replace(
                    'https://litlfred.github.io/notebooks/weierstrass-playground/',
                    f'{self.base_url}/weierstrass-playground/'
                )
                content = content.replace(
                    'https://litlfred.github.io/notebooks/notebooks/',
                    f'{self.base_url}/notebooks/'
                )
                # Keep schema URLs pointing to production
                content = content.replace(
                    f'{self.base_url}/schema/',
                    f'{self.schema_base_url}/schema/'
                )
            
            # Update JSON-LD files
            elif file_path.suffix in ['.json', '.jsonld']:
                try:
                    data = json.loads(content)
                    updated_data = self.update_json_urls(data)
                    content = json.dumps(updated_data, indent=2)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as text
                    content = self.update_text_urls(content)
            
            # Update HTML files
            elif file_path.suffix == '.html':
                content = self.update_text_urls(content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ Updated URLs in: {file_path.relative_to(self.repo_root)}")
                
        except Exception as e:
            print(f"  ⚠️  Error updating {file_path}: {e}")

    def update_json_urls(self, data):
        """Update URLs in JSON data structure"""
        if isinstance(data, str):
            # Update resource URLs but keep schema URLs absolute
            if data.startswith('https://litlfred.github.io/notebooks/'):
                if '/schema/' in data:
                    # Keep schema URLs pointing to production
                    return data
                else:
                    # Update other URLs to current deployment
                    return data.replace('https://litlfred.github.io/notebooks', self.base_url)
            return data
        elif isinstance(data, list):
            return [self.update_json_urls(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.update_json_urls(value) for key, value in data.items()}
        else:
            return data

    def update_text_urls(self, content):
        """Update URLs in text content"""
        # Update resource URLs but keep schema URLs absolute
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if 'https://litlfred.github.io/notebooks/' in line and '/schema/' not in line:
                line = line.replace('https://litlfred.github.io/notebooks', self.base_url)
            updated_lines.append(line)
        
        return '\n'.join(updated_lines)

    def create_deployment_manifest(self) -> Dict[str, Any]:
        """Create deployment manifest with environment info"""
        return {
            "deployment": {
                "timestamp": self.get_timestamp(),
                "branch": self.branch_name,
                "type": "production" if self.is_production else "preview",
                "base_url": self.base_url,
                "schema_base_url": self.schema_base_url,
                "deployment_path": self.deployment_path,
                "repository": f"{self.repo_owner}/{self.repo_name}"
            },
            "environment": {
                "DEPLOYMENT_TYPE": "production" if self.is_production else "preview",
                "GITHUB_PAGES_BASE_URL": self.base_url,
                "SCHEMA_BASE_URL": self.schema_base_url,
                "DEPLOYMENT_CONTEXT": "production" if self.is_production else "preview"
            }
        }

    def write_deployment_manifest(self, deploy_dir: Path, manifest: Dict[str, Any]):
        """Write deployment manifest to deployment directory"""
        manifest_file = deploy_dir / "deployment-manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  ✓ Created deployment manifest: {manifest_file}")

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main function"""
    # Get parameters from environment or command line
    repo_root = os.getenv('GITHUB_WORKSPACE', os.getcwd())
    branch_name = os.getenv('GITHUB_REF_NAME', 'main')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'litlfred')
    repo_name = os.getenv('GITHUB_REPOSITORY', 'litlfred/notebooks').split('/')[-1]
    
    # Command line arguments override environment
    if len(sys.argv) > 1:
        branch_name = sys.argv[1]
    if len(sys.argv) > 2:
        repo_root = sys.argv[2]
    
    print(f"🌿 Deploying branch: {branch_name}")
    print(f"📁 Repository root: {repo_root}")
    
    deployer = PreviewBranchDeployer(repo_root, branch_name, repo_owner, repo_name)
    manifest = deployer.prepare_preview_deployment()
    
    print("\n🎉 Preview deployment preparation complete!")
    print(f"📊 Deployment type: {manifest['deployment']['type']}")
    print(f"🔗 Base URL: {manifest['deployment']['base_url']}")
    print(f"📋 Manifest: {manifest}")

if __name__ == "__main__":
    main()