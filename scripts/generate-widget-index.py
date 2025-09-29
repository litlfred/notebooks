#!/usr/bin/env python3
"""
Auto-generate index.html files for widgets
Implements the auto-generation requirement from the original issue
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

class WidgetIndexGenerator:
    """Generate index.html files for widgets automatically"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.templates_dir = self.repo_root / "scripts" / "templates"
        self.widgets_dir = self.repo_root / "libraries"
        
    def discover_widgets(self) -> List[Dict[str, Any]]:
        """Discover all widgets in the repository"""
        widgets = []
        
        # Scan library directories for widgets
        for library_dir in self.widgets_dir.iterdir():
            if not library_dir.is_dir():
                continue
                
            # Look for widget directories
            for widget_dir in library_dir.iterdir():
                if not widget_dir.is_dir():
                    continue
                    
                # Check if this is a widget (has schema files)
                widget_schema_file = widget_dir / "widget.schema.json"
                if widget_schema_file.exists():
                    widget_info = self.extract_widget_info(widget_dir)
                    if widget_info:
                        widgets.append(widget_info)
        
        # Add special case for root playground widget
        playground_widget = {
            'id': 'weierstrass-playground',
            'name': '℘ Weierstrass Playground',
            'path': self.repo_root,
            'type': 'playground',
            'library': 'root',
            'config': {
                'playgroundPath': 'docs/weierstrass-playground/board.html',
                'threadPoolWorkers': 4,
                'enableLazyLoading': True,
                'preloadScientific': True,
                'showLoadingScreen': True,
                'loadingDelay': 1000
            }
        }
        widgets.append(playground_widget)
        
        return widgets
    
    def extract_widget_info(self, widget_dir: Path) -> Dict[str, Any]:
        """Extract widget information from directory"""
        try:
            # Read widget schema
            widget_schema_file = widget_dir / "widget.schema.json"
            if not widget_schema_file.exists():
                return None
                
            with open(widget_schema_file, 'r') as f:
                schema = json.load(f)
            
            # Extract basic info
            widget_id = widget_dir.name
            widget_name = schema.get('title', widget_id.replace('-', ' ').title())
            library_name = widget_dir.parent.name
            
            # Determine widget type
            widget_type = 'widget'
            if 'notebook' in widget_id.lower():
                widget_type = 'notebook'
            elif 'playground' in widget_id.lower():
                widget_type = 'playground'
            elif any(viz_term in widget_id.lower() for viz_term in ['plot', 'chart', 'graph', 'visual']):
                widget_type = 'visualization'
            elif 'python' in widget_id.lower() or 'code' in widget_id.lower():
                widget_type = 'computation'
            
            return {
                'id': widget_id,
                'name': widget_name,
                'path': widget_dir,
                'type': widget_type,
                'library': library_name,
                'schema': schema,
                'config': self.extract_widget_config(schema)
            }
            
        except Exception as e:
            print(f"Warning: Could not extract info for {widget_dir}: {e}")
            return None
    
    def extract_widget_config(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract widget configuration from schema"""
        return {
            'threadPoolWorkers': 2,  # Default for individual widgets
            'enableLazyLoading': True,
            'showLoadingScreen': True,
            'loadingDelay': 500
        }
    
    def generate_widget_index(self, widget: Dict[str, Any]) -> str:
        """Generate index.html content for a widget"""
        template = self.load_template(widget['type'])
        
        # Replace template variables
        content = template.format(
            widget_id=widget['id'],
            widget_name=widget['name'],
            widget_type=widget['type'],
            library_name=widget['library'],
            thread_pool_workers=widget['config']['threadPoolWorkers'],
            enable_lazy_loading=str(widget['config']['enableLazyLoading']).lower(),
            show_loading_screen=str(widget['config']['showLoadingScreen']).lower(),
            loading_delay=widget['config']['loadingDelay'],
            playground_path=widget['config'].get('playgroundPath', f'../{widget["id"]}.html'),
            relative_js_path='../../js' if widget['library'] != 'root' else 'js'
        )
        
        return content
    
    def load_template(self, widget_type: str) -> str:
        """Load HTML template for widget type"""
        template_file = self.templates_dir / f"{widget_type}-index.html"
        
        if not template_file.exists():
            template_file = self.templates_dir / "default-index.html"
        
        if not template_file.exists():
            return self.get_default_template()
        
        with open(template_file, 'r') as f:
            return f.read()
    
    def get_default_template(self) -> str:
        """Get default index.html template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{widget_name} - Mathematical Widget</title>
    <link rel="stylesheet" href="{relative_js_path}/minimal-launcher-styles.css">
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-container" class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">Initializing {widget_name}</div>
        <div class="loading-details" id="loading-details">
            Setting up widget execution environment...
        </div>
    </div>

    <!-- Error Overlay -->
    <div id="error-container" class="error-container">
        <div class="error-content">
            <div class="error-title">Widget Loading Error</div>
            <div class="error-message" id="error-message">
                Failed to load the {widget_name} widget.
            </div>
            <div class="error-details" id="error-details"></div>
            <div class="shutdown-links">
                <a href="javascript:window.location.reload()" class="shutdown-link">🔄 Retry</a>
                <a href="../index.html" class="shutdown-link">🏠 Home</a>
                <a href="https://github.com/litlfred/notebooks" class="shutdown-link" target="_blank">💻 GitHub</a>
            </div>
        </div>
    </div>

    <script src="{relative_js_path}/github-pages-launcher.js"></script>
    <script>
        // Initialize widget launcher
        document.addEventListener('DOMContentLoaded', () => {{
            const launcher = GitHubPagesLauncher.createForGitHubPages({{
                threadPoolWorkers: {thread_pool_workers},
                enableLazyLoading: {enable_lazy_loading},
                showLoadingScreen: {show_loading_screen},
                loadingDelay: {loading_delay},
                playgroundPath: '{playground_path}'
            }});
            launcher.launch();
        }});
    </script>
</body>
</html>'''
    
    def generate_all_widget_indexes(self):
        """Generate index.html files for all discovered widgets"""
        widgets = self.discover_widgets()
        generated_files = []
        
        print(f"Discovered {len(widgets)} widgets:")
        for widget in widgets:
            print(f"  - {widget['id']} ({widget['type']}) in {widget['library']}")
        
        print("\nGenerating index.html files...")
        
        for widget in widgets:
            try:
                # Generate content
                content = self.generate_widget_index(widget)
                
                # Determine output path
                if widget['library'] == 'root':
                    # Root playground widget uses main index.html (already exists)
                    output_path = self.repo_root / "index.html"
                    print(f"  ✓ Skipping {widget['id']} (root index.html already exists)")
                    continue
                else:
                    # Create widget-specific index.html
                    output_path = widget['path'] / "index.html"
                
                # Write file
                with open(output_path, 'w') as f:
                    f.write(content)
                
                generated_files.append(str(output_path))
                print(f"  ✓ Generated {output_path}")
                
            except Exception as e:
                print(f"  ✗ Failed to generate index for {widget['id']}: {e}")
        
        print(f"\nGenerated {len(generated_files)} index.html files:")
        for file_path in generated_files:
            print(f"  - {file_path}")
        
        return generated_files
    
    def create_templates(self):
        """Create template files if they don't exist"""
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create playground template
        playground_template = self.templates_dir / "playground-index.html"
        if not playground_template.exists():
            with open(playground_template, 'w') as f:
                f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{widget_name}</title>
    <link rel="stylesheet" href="{relative_js_path}/minimal-launcher-styles.css">
</head>
<body>
    <div id="loading-container" class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">Initializing {widget_name}</div>
        <div class="loading-details" id="loading-details">
            Setting up mathematical workspace...
        </div>
    </div>

    <div id="error-container" class="error-container">
        <div class="error-content">
            <div class="error-title">Playground Loading Error</div>
            <div class="error-message" id="error-message">
                Failed to load the mathematical playground.
            </div>
            <div class="error-details" id="error-details"></div>
            <div class="shutdown-links">
                <a href="javascript:window.location.reload()" class="shutdown-link">🔄 Retry</a>
                <a href="{playground_path}" class="shutdown-link">🎯 Direct Access</a>
                <a href="https://github.com/litlfred/notebooks" class="shutdown-link" target="_blank">💻 GitHub</a>
            </div>
        </div>
    </div>

    <script src="{relative_js_path}/github-pages-launcher.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const launcher = GitHubPagesLauncher.createForGitHubPages({{
                threadPoolWorkers: {thread_pool_workers},
                enableLazyLoading: {enable_lazy_loading},
                preloadScientific: true,
                playgroundPath: '{playground_path}',
                showLoadingScreen: {show_loading_screen},
                loadingDelay: {loading_delay}
            }});
            launcher.launch();
        }});
    </script>
</body>
</html>''')

def main():
    """Main function"""
    if len(sys.argv) < 2:
        repo_root = os.getcwd()
    else:
        repo_root = sys.argv[1]
    
    print(f"Widget Index Generator")
    print(f"Repository: {repo_root}")
    print("=" * 50)
    
    generator = WidgetIndexGenerator(repo_root)
    
    # Create templates
    generator.create_templates()
    
    # Generate all widget index files
    generated_files = generator.generate_all_widget_indexes()
    
    print("\n" + "=" * 50)
    print(f"Index generation complete! Generated {len(generated_files)} files.")

if __name__ == "__main__":
    main()