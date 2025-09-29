#!/usr/bin/env python3
"""
URL Service for GitHub Pages Deployment
Manages environment-aware URL generation for production and preview deployments
"""

import os
import json
import re
from typing import Dict, Optional, Any
from pathlib import Path


class URLService:
    """Service for generating deployment-aware URLs"""
    
    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Get deployment configuration from environment variables
        self.github_repository = os.getenv('GITHUB_REPOSITORY', 'litlfred/notebooks')
        self.github_ref_name = os.getenv('GITHUB_REF_NAME', 'main')
        self.deployment_type = os.getenv('DEPLOYMENT_TYPE', 'preview')  # 'production' or 'preview'
        
        # Parse owner and repo from repository name
        parts = self.github_repository.split('/')
        self.owner = parts[0] if len(parts) > 0 else 'litlfred'
        self.repo = parts[1] if len(parts) > 1 else 'notebooks'
        
        # Generate base URL based on deployment type
        self.base_url = self._generate_base_url()
    
    def _generate_base_url(self) -> str:
        """Generate base URL based on deployment environment"""
        github_pages_base = f"https://{self.owner}.github.io/{self.repo}"
        
        if self.deployment_type == 'production':
            # Production deployment: {profile}.github.io/{repo}
            return github_pages_base
        else:
            # Preview deployment: {profile}.github.io/{repo}/branch-preview/{branch-name}
            safe_branch_name = self._sanitize_branch_name(self.github_ref_name)
            return f"{github_pages_base}/branch-preview/{safe_branch_name}"
    
    def _sanitize_branch_name(self, branch_name: str) -> str:
        """Sanitize branch name for URL usage"""
        # Replace invalid URL characters with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', branch_name)
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')
    
    def get_base_url(self) -> str:
        """Get the base URL for this deployment"""
        return self.base_url
    
    def get_schema_url(self, schema_path: str) -> str:
        """Generate URL for a schema file"""
        # Remove leading slash if present
        schema_path = schema_path.lstrip('/')
        return f"{self.base_url}/{schema_path}"
    
    def get_library_url(self, library_name: str, file_path: str = '') -> str:
        """Generate URL for a library resource"""
        file_path = file_path.lstrip('/')
        if file_path:
            return f"{self.base_url}/libraries/{library_name}/{file_path}"
        else:
            return f"{self.base_url}/libraries/{library_name}/"
    
    def get_widget_url(self, widget_id: str) -> str:
        """Generate URL for a widget"""
        return f"{self.base_url}/widgets/{widget_id}/"
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information"""
        return {
            "deployment_type": self.deployment_type,
            "base_url": self.base_url,
            "repository": self.github_repository,
            "branch": self.github_ref_name,
            "owner": self.owner,
            "repo": self.repo,
            "sanitized_branch": self._sanitize_branch_name(self.github_ref_name)
        }
    
    def update_schema_urls(self, schema_content: str) -> str:
        """Update hardcoded URLs in schema content to be environment-aware"""
        # Replace hardcoded GitHub Pages URLs with relative or environment-aware URLs
        old_base = f"https://{self.owner}.github.io/{self.repo}"
        
        # Replace absolute URLs with relative paths where possible
        updated_content = schema_content.replace(old_base, self.base_url)
        
        return updated_content
    
    def generate_url_config(self) -> Dict[str, Any]:
        """Generate URL configuration for frontend"""
        return {
            "baseUrl": self.base_url,
            "deploymentType": self.deployment_type,
            "repository": self.github_repository,
            "branch": self.github_ref_name,
            "owner": self.owner,
            "repo": self.repo,
            "urls": {
                "schemas": f"{self.base_url}/schema/",
                "libraries": f"{self.base_url}/libraries/",
                "widgets": f"{self.base_url}/widgets/",
                "notebooks": f"{self.base_url}/notebooks/"
            }
        }
    
    def write_url_config(self, output_path: Optional[str] = None) -> str:
        """Write URL configuration to file"""
        if not output_path:
            output_path = self.repo_root / "docs" / "deployment-config.json"
        
        config = self.generate_url_config()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ URL configuration written to: {output_file}")
        return str(output_file)


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate URL configuration for deployment')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--deployment-type', choices=['production', 'preview'], 
                      help='Override deployment type')
    parser.add_argument('--branch', help='Override branch name')
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.deployment_type:
        os.environ['DEPLOYMENT_TYPE'] = args.deployment_type
    if args.branch:
        os.environ['GITHUB_REF_NAME'] = args.branch
    
    service = URLService(args.repo_root)
    
    print("🌐 URL Service Configuration")
    print("=" * 40)
    
    info = service.get_deployment_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n📋 Generated URLs:")
    config = service.generate_url_config()
    for category, url in config['urls'].items():
        print(f"  {category}: {url}")
    
    # Write configuration file
    config_file = service.write_url_config(args.output)
    
    print(f"\n✅ URL service initialized successfully")
    print(f"📁 Configuration: {config_file}")


if __name__ == "__main__":
    main()