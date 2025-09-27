#!/usr/bin/env python3
"""
Deployment Manager for GitHub Pages Branch Previews
Handles URL generation and Jekyll configuration based on deployment context
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class DeploymentManager:
    """Manages deployment configuration for GitHub Pages with branch previews"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.docs_dir = self.repo_root / "docs"
        self.schema_dir = self.docs_dir / "schema"
        
    def get_deployment_context(self) -> Dict[str, Any]:
        """Determine deployment context from environment variables"""
        github_ref = os.getenv('GITHUB_REF', '')
        github_event_name = os.getenv('GITHUB_EVENT_NAME', '')
        workflow_dispatch_input = os.getenv('INPUT_DEPLOY_TYPE', '')
        
        # Parse branch name from ref
        branch_name = 'main'
        if github_ref.startswith('refs/heads/'):
            branch_name = github_ref.replace('refs/heads/', '')
        elif github_ref.startswith('refs/pull/'):
            # For PR previews, use PR number format
            pr_number = github_ref.split('/')[2]
            branch_name = f"pr-{pr_number}"
        
        # Determine deployment type
        is_production = (
            workflow_dispatch_input == 'production' or
            (github_event_name == 'workflow_dispatch' and branch_name == 'main')
        )
        
        profile = os.getenv('GITHUB_REPOSITORY_OWNER', 'litlfred')
        repo = os.getenv('GITHUB_REPOSITORY', 'litlfred/notebooks').split('/')[-1]
        
        if is_production:
            base_url = f"https://{profile}.github.io/{repo}"
            baseurl = f"/{repo}"
            deployment_type = "production"
        else:
            base_url = f"https://{profile}.github.io/{repo}/branch-preview/{branch_name}"
            baseurl = f"/{repo}/branch-preview/{branch_name}"
            deployment_type = "preview"
        
        return {
            'profile': profile,
            'repo': repo,
            'branch_name': branch_name,
            'base_url': base_url,
            'baseurl': baseurl,
            'deployment_type': deployment_type,
            'is_production': is_production,
            'schema_base_url': f"{base_url}/schema"
        }
    
    def update_jekyll_config(self, context: Dict[str, Any]) -> None:
        """Update Jekyll _config.yml with deployment-specific settings"""
        config_path = self.docs_dir / "_config.yml"
        
        # Read existing config
        config_content = ""
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_content = f.read()
        
        # Update or add deployment-specific settings
        new_lines = []
        baseurl_set = False
        url_set = False
        
        for line in config_content.split('\n'):
            if line.startswith('baseurl:'):
                new_lines.append(f'baseurl: "{context["baseurl"]}"')
                baseurl_set = True
            elif line.startswith('url:'):
                new_lines.append(f'url: "https://{context["profile"]}.github.io"')
                url_set = True
            else:
                new_lines.append(line)
        
        # Add missing settings
        if not baseurl_set:
            new_lines.append(f'baseurl: "{context["baseurl"]}"')
        if not url_set:
            new_lines.append(f'url: "https://{context["profile"]}.github.io"')
        
        # Add deployment context info
        new_lines.extend([
            '',
            '# Deployment context (auto-generated)',
            f'deployment_type: "{context["deployment_type"]}"',
            f'branch_name: "{context["branch_name"]}"',
            f'schema_base_url: "{context["schema_base_url"]}"'
        ])
        
        # Write updated config
        with open(config_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Updated Jekyll config for {context['deployment_type']} deployment")
        print(f"   Base URL: {context['base_url']}")
    
    def update_schema_urls(self, context: Dict[str, Any]) -> None:
        """Update schema files with deployment-aware URLs"""
        if not self.schema_dir.exists():
            print("ℹ️  No schema directory found, skipping schema URL updates")
            return
        
        schema_base = context['schema_base_url']
        files_updated = 0
        
        # Find all JSON and JSON-LD files
        for json_file in self.schema_dir.rglob("*.json"):
            if self._update_json_file_urls(json_file, schema_base):
                files_updated += 1
        
        for jsonld_file in self.schema_dir.rglob("*.jsonld"):
            if self._update_json_file_urls(jsonld_file, schema_base):
                files_updated += 1
        
        print(f"✅ Updated {files_updated} schema files with deployment URLs")
    
    def _update_json_file_urls(self, file_path: Path, schema_base: str) -> bool:
        """Update template variables and hardcoded URLs in JSON/JSON-LD files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Replace template variables first
            content = content.replace('{{SCHEMA_BASE_URL}}', schema_base)
            
            # For backwards compatibility, also handle hardcoded URLs
            old_patterns = [
                'https://litlfred.github.io/notebooks/schema',
            ]
            
            for old_pattern in old_patterns:
                content = content.replace(old_pattern, schema_base)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            print(f"⚠️  Error updating {file_path}: {e}")
        
        return False
    
    def create_deployment_info(self, context: Dict[str, Any]) -> None:
        """Create deployment info file for JavaScript access"""
        info_file = self.docs_dir / "deployment-info.json"
        
        deployment_info = {
            "deployment_type": context["deployment_type"],
            "branch_name": context["branch_name"],
            "base_url": context["base_url"],
            "schema_base_url": context["schema_base_url"],
            "is_production": context["is_production"]
        }
        
        with open(info_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"✅ Created deployment info file: {info_file}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python deploy_manager.py <repo_root_path> [action]")
        print("Actions: configure (default), info")
        sys.exit(1)
    
    repo_root = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "configure"
    
    manager = DeploymentManager(repo_root)
    context = manager.get_deployment_context()
    
    print(f"🚀 Deployment Manager")
    print(f"   Type: {context['deployment_type']}")
    print(f"   Branch: {context['branch_name']}")
    print(f"   Base URL: {context['base_url']}")
    
    if action == "configure":
        manager.update_jekyll_config(context)
        manager.update_schema_urls(context)
        manager.create_deployment_info(context)
        print("✅ Deployment configuration complete")
    
    elif action == "info":
        print("\nDeployment Context:")
        for key, value in context.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()