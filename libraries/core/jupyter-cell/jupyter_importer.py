"""
Jupyter Notebook Importer
Converts Jupyter notebooks (.ipynb) to widget framework format
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class JupyterNotebookImporter:
    """
    Imports Jupyter notebooks and converts cells to widget instances
    with sequential arrow connections
    """
    
    def __init__(self):
        self.supported_cell_types = ['markdown', 'code']
    
    def import_notebook(self, notebook_data: Dict[str, Any], import_mode: str = 'import') -> Dict[str, Any]:
        """
        Import a Jupyter notebook and convert to widget framework format
        
        Args:
            notebook_data: Parsed Jupyter notebook JSON
            import_mode: 'import' for editable copy, 'link' for read-only reference
            
        Returns:
            JSON-LD formatted notebook with widget instances and arrows
        """
        
        # Extract notebook metadata
        metadata = notebook_data.get('metadata', {})
        cells = notebook_data.get('cells', [])
        
        # Generate base IDs
        notebook_id = f"urn:notebook:{str(uuid.uuid4())}"
        
        # Convert cells to widgets
        widgets = []
        connections = []
        
        previous_widget_id = None
        
        for i, cell in enumerate(cells):
            if cell.get('cell_type') not in self.supported_cell_types:
                continue  # Skip unsupported cell types
            
            widget_data = self.convert_cell_to_widget(cell, i, import_mode)
            widgets.append(widget_data)
            
            # Create arrow connection to previous cell
            if previous_widget_id:
                connection = self.create_sequential_arrow(previous_widget_id, widget_data['@id'], i)
                connections.append(connection)
            
            previous_widget_id = widget_data['@id']
        
        # Create notebook JSON-LD structure
        jsonld_notebook = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/libraries/core/common/context.jsonld"
            ],
            "@id": notebook_id,
            "@type": ["prov:Entity", "jupyter:notebook"],
            "dct:title": metadata.get('title', 'Imported Jupyter Notebook'),
            "dct:description": f"Notebook imported in {import_mode} mode with {len(widgets)} cells",
            "jupyter:nbformat": notebook_data.get('nbformat', 4),
            "jupyter:nbformat_minor": notebook_data.get('nbformat_minor', 0),
            "jupyter:kernelspec": metadata.get('kernelspec', {}),
            "jupyter:language_info": metadata.get('language_info', {}),
            "jupyter:import_mode": import_mode,
            "prov:generatedAtTime": datetime.now().isoformat() + "Z",
            "@graph": widgets + connections
        }
        
        return jsonld_notebook
    
    def convert_cell_to_widget(self, cell: Dict[str, Any], cell_index: int, import_mode: str) -> Dict[str, Any]:
        """Convert a Jupyter cell to a widget instance"""
        
        cell_type = cell.get('cell_type')
        cell_id = f"urn:widget:jupyter-{cell_type}-cell-{cell_index}"
        
        # Extract cell content
        source = cell.get('source', [])
        if isinstance(source, list):
            content = ''.join(source)
        else:
            content = str(source)
        
        # Base widget data
        widget_data = {
            "@id": cell_id,
            "@type": ["prov:Entity", f"jupyter:{cell_type}-cell", "widget:instance"],
            "dct:conformsTo": f"https://litlfred.github.io/notebooks/libraries/core/jupyter-cell/{cell_type}-input.schema.json",
            "jupyter:cell_index": cell_index,
            "jupyter:cell_type": cell_type,
            "jupyter:import_mode": import_mode,
            "widget:position": {
                "x": 100 + (cell_index % 3) * 350,
                "y": 100 + (cell_index // 3) * 300
            },
            "widget:size": {
                "width": 320,
                "height": 250
            },
            "prov:generatedAtTime": datetime.now().isoformat() + "Z"
        }
        
        if cell_type == 'markdown':
            widget_data.update({
                "widget:type": "jupyter-markdown-cell",
                "input": {
                    "@id": f"{cell_id}:input",
                    "@type": ["prov:Entity", "jupyter:markdown-input"],
                    "content": content,
                    "show_note": True,
                    "cell_metadata": cell.get('metadata', {}),
                    "attachments": cell.get('attachments', {}),
                    "cell_index": cell_index
                }
            })
        
        elif cell_type == 'code':
            widget_data.update({
                "widget:type": "jupyter-code-cell",
                "input": {
                    "@id": f"{cell_id}:input",
                    "@type": ["prov:Entity", "jupyter:code-input"],
                    "code": content,
                    "execute_immediately": False,
                    "cell_metadata": cell.get('metadata', {}),
                    "outputs": cell.get('outputs', []),
                    "execution_count": cell.get('execution_count'),
                    "cell_index": cell_index
                }
            })
        
        return widget_data
    
    def create_sequential_arrow(self, source_widget_id: str, target_widget_id: str, target_index: int) -> Dict[str, Any]:
        """Create an arrow connection between sequential cells"""
        
        connection_id = f"urn:connection:sequential-{target_index}"
        
        return {
            "@id": connection_id,
            "@type": ["prov:Entity", "workflow:Connection", "jupyter:sequential-arrow"],
            "dct:conformsTo": "https://litlfred.github.io/notebooks/libraries/core/arrow/input.schema.json",
            "workflow:connection_type": "sequential_flow",
            "jupyter:connection_reason": "Sequential execution order in notebook",
            "source": {
                "widget": source_widget_id,
                "output": f"{source_widget_id}:output"
            },
            "target": {
                "widget": target_widget_id,
                "input": f"{target_widget_id}:input"
            },
            "visual": {
                "arrow_style": "sequential",
                "color": "#4A90E2",
                "label": f"Cell {target_index - 1} → {target_index}"
            },
            "prov:generatedAtTime": datetime.now().isoformat() + "Z"
        }
    
    def import_from_url(self, url: str, import_mode: str = 'link') -> Dict[str, Any]:
        """
        Import notebook from URL
        
        Args:
            url: URL to Jupyter notebook (.ipynb)
            import_mode: 'import' for editable copy, 'link' for read-only reference
        """
        import urllib.request
        import urllib.error
        
        try:
            with urllib.request.urlopen(url) as response:
                notebook_data = json.loads(response.read().decode('utf-8'))
            
            # Add URL metadata
            result = self.import_notebook(notebook_data, import_mode)
            result['jupyter:source_url'] = url
            result['jupyter:fetched_at'] = datetime.now().isoformat() + "Z"
            
            return result
            
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch notebook from URL: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in notebook: {e}")
    
    def import_from_file(self, file_content: str, filename: str = 'notebook.ipynb') -> Dict[str, Any]:
        """
        Import notebook from file content
        
        Args:
            file_content: Raw notebook file content
            filename: Original filename
        """
        try:
            notebook_data = json.loads(file_content)
            
            result = self.import_notebook(notebook_data, 'import')
            result['jupyter:source_filename'] = filename
            result['jupyter:imported_at'] = datetime.now().isoformat() + "Z"
            
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in notebook file: {e}")
    
    def validate_notebook_format(self, notebook_data: Dict[str, Any]) -> bool:
        """Validate that the data is a valid Jupyter notebook"""
        required_fields = ['cells', 'metadata', 'nbformat']
        
        for field in required_fields:
            if field not in notebook_data:
                return False
        
        # Check nbformat version
        nbformat = notebook_data.get('nbformat', 0)
        if nbformat < 3:  # Support nbformat 3 and above
            return False
        
        # Check cells structure
        cells = notebook_data.get('cells', [])
        if not isinstance(cells, list):
            return False
        
        for cell in cells:
            if not isinstance(cell, dict):
                return False
            if 'cell_type' not in cell:
                return False
        
        return True
    
    def get_notebook_preview(self, notebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a preview of the notebook for display before import"""
        if not self.validate_notebook_format(notebook_data):
            return {
                'valid': False,
                'error': 'Invalid notebook format'
            }
        
        cells = notebook_data.get('cells', [])
        metadata = notebook_data.get('metadata', {})
        
        cell_summary = {}
        for cell in cells:
            cell_type = cell.get('cell_type', 'unknown')
            cell_summary[cell_type] = cell_summary.get(cell_type, 0) + 1
        
        return {
            'valid': True,
            'title': metadata.get('title', 'Untitled Notebook'),
            'language': metadata.get('language_info', {}).get('name', 'unknown'),
            'kernel': metadata.get('kernelspec', {}).get('display_name', 'unknown'),
            'total_cells': len(cells),
            'cell_types': cell_summary,
            'nbformat': f"{notebook_data.get('nbformat', 0)}.{notebook_data.get('nbformat_minor', 0)}"
        }


# Global importer instance
jupyter_importer = JupyterNotebookImporter()