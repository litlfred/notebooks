#!/usr/bin/env python3
"""
Update Schema URLs
Updates hardcoded URLs in schema and JSON-LD files to be environment-aware
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from url_service import URLService


def find_schema_files(repo_root: Path) -> List[Path]:
    """Find all schema and JSON-LD files"""
    patterns = ['*.schema.json', '*.jsonld', '*.json']
    
    files = []
    for pattern in patterns:
        files.extend(repo_root.rglob(pattern))
    
    # Filter to relevant files
    schema_files = []
    for file_path in files:
        rel_path = str(file_path.relative_to(repo_root)).lower()
        
        # Include schema files, JSON-LD files, and configuration files
        if any(keyword in rel_path for keyword in [
            'schema', 'jsonld', 'manifest', 'config', 'widget'
        ]):
            # Exclude build directories and temporary files
            if not any(exclude in rel_path for exclude in [
                '_build/', 'node_modules/', '.git/', '__pycache__/', 'temp'
            ]):
                schema_files.append(file_path)
    
    return schema_files


def update_file_urls(file_path: Path, url_service: URLService) -> bool:
    """Update URLs in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update hardcoded GitHub Pages URLs
        old_patterns = [
            r'https://litlfred\.github\.io/notebooks',
            r'https://[^.]+\.github\.io/[^/]+',
        ]
        
        for pattern in old_patterns:
            # For schema URLs, keep them as relative paths where possible
            if 'schema' in str(file_path) or 'jsonld' in str(file_path):
                # Replace absolute schema URLs with relative ones
                content = re.sub(
                    pattern + r'/schema/',
                    './schema/',
                    content
                )
                # Replace absolute library URLs with relative ones
                content = re.sub(
                    pattern + r'/libraries/',
                    './libraries/',
                    content
                )
            
            # For manifest and config files, use environment-aware URLs
            if 'manifest' in str(file_path) or 'config' in str(file_path):
                base_url = url_service.get_base_url()
                content = re.sub(pattern, base_url, content)
        
        # Update specific hardcoded URLs to use relative paths
        replacements = {
            '"https://litlfred.github.io/notebooks/': f'"{url_service.get_base_url()}/',
            '"https://litlfred.github.io/notebooks"': f'"{url_service.get_base_url()}"',
        }
        
        for old_url, new_url in replacements.items():
            content = content.replace(old_url, new_url)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error updating {file_path}: {e}")
        return False


def update_all_schema_urls(repo_root: str) -> Dict[str, Any]:
    """Update all schema URLs in the repository"""
    repo_path = Path(repo_root)
    url_service = URLService(repo_root)
    
    print("🔄 Updating schema URLs for environment-aware deployment")
    print("=" * 60)
    
    deployment_info = url_service.get_deployment_info()
    print(f"🎯 Deployment type: {deployment_info['deployment_type']}")
    print(f"🔗 Base URL: {deployment_info['base_url']}")
    print(f"🌿 Branch: {deployment_info['branch']}")
    
    # Find all schema files
    schema_files = find_schema_files(repo_path)
    print(f"\n📁 Found {len(schema_files)} schema/config files")
    
    updated_files = []
    for file_path in schema_files:
        rel_path = file_path.relative_to(repo_path)
        print(f"  📄 Checking: {rel_path}")
        
        if update_file_urls(file_path, url_service):
            updated_files.append(str(rel_path))
            print(f"    ✓ Updated")
        else:
            print(f"    - No changes needed")
    
    print(f"\n📊 Results:")
    print(f"  📄 Files checked: {len(schema_files)}")
    print(f"  ✏️  Files updated: {len(updated_files)}")
    
    if updated_files:
        print(f"\n📝 Updated files:")
        for file_path in updated_files:
            print(f"    • {file_path}")
    
    return {
        "deployment_info": deployment_info,
        "files_checked": len(schema_files),
        "files_updated": len(updated_files),
        "updated_files": updated_files
    }


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update schema URLs for deployment')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    parser.add_argument('--deployment-type', choices=['production', 'preview'], 
                      help='Override deployment type')
    parser.add_argument('--branch', help='Override branch name')
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.deployment_type:
        os.environ['DEPLOYMENT_TYPE'] = args.deployment_type
    if args.branch:
        os.environ['GITHUB_REF_NAME'] = args.branch
    
    # Update schema URLs
    results = update_all_schema_urls(args.repo_root)
    
    print(f"\n✅ Schema URL update completed")
    
    if results['files_updated'] > 0:
        print(f"🔄 {results['files_updated']} files were updated")
        print("💡 Remember to commit these changes")
    else:
        print("ℹ️  No files needed updating")


if __name__ == "__main__":
    main()