/**
 * Notebook Loader for Mathematical Workspace
 * Handles JSON-LD notebook loading, saving, and file management
 */

class NotebookLoader {
    constructor(boardApp) {
        this.boardApp = boardApp;
        this.setupFileHandlers();
        this.loadAvailableNotebooks();
    }

    /**
     * Setup file input handlers for notebook loading
     */
    setupFileHandlers() {
        // Create file input for loading
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.jsonld,.json,.ipynb';
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', this.handleFileLoad.bind(this));
        document.body.appendChild(fileInput);
        this.fileInput = fileInput;

        // Setup drag and drop
        const boardContent = document.getElementById('board-content');
        boardContent.addEventListener('dragover', this.handleDragOver.bind(this));
        boardContent.addEventListener('drop', this.handleDrop.bind(this));
    }

    /**
     * Load available notebooks from notebooks/ directory
     */
    async loadAvailableNotebooks() {
        try {
            // Try to fetch from GitHub API (for GitHub Pages deployment)
            await this.loadFromGitHub();
            
            // Fallback to static list if GitHub API fails
            if (this.availableNotebooks.length === 0) {
                this.availableNotebooks = [
                    {
                        filename: 'example-weierstrass-workflow.jsonld',
                        title: 'Weierstrass Function Analysis with p=5, q=7',
                        description: 'Complete mathematical workflow demonstrating PQ-Torus lattice parameters',
                        modified: '2024-01-15T12:15:00Z',
                        type: 'jsonld'
                    },
                    {
                        filename: 'sample-mathematical-analysis.ipynb',
                        title: 'Mathematical Analysis Demo',
                        description: 'Sample Jupyter notebook with mathematical computations',
                        modified: '2024-01-15T14:30:00Z',
                        type: 'ipynb'
                    }
                ];
            }
            
            this.updateNotebookList();
        } catch (error) {
            console.error('Failed to load available notebooks:', error);
        }
    }

    /**
     * Load notebooks from GitHub repository
     */
    async loadFromGitHub() {
        try {
            // Get repository info from current URL
            const repoInfo = this.getRepositoryInfo();
            if (!repoInfo) return;

            const apiUrl = `https://api.github.com/repos/${repoInfo.owner}/${repoInfo.repo}/contents/notebooks`;
            
            const response = await fetch(apiUrl);
            if (!response.ok) {
                console.log('GitHub API not available, using static list');
                return;
            }

            const files = await response.json();
            this.availableNotebooks = [];

            for (const file of files) {
                if (file.type === 'file') {
                    const extension = file.name.split('.').pop().toLowerCase();
                    if (['ipynb', 'jsonld', 'json'].includes(extension)) {
                        const notebook = {
                            filename: file.name,
                            title: this.generateTitleFromFilename(file.name),
                            description: `${extension.toUpperCase()} notebook (${Math.round(file.size / 1024)}KB)`,
                            modified: file.sha ? 'From GitHub' : 'Unknown',
                            type: extension,
                            download_url: file.download_url,
                            github_url: file.html_url
                        };
                        this.availableNotebooks.push(notebook);
                    }
                }
            }

            console.log(`Loaded ${this.availableNotebooks.length} notebooks from GitHub`);
            
        } catch (error) {
            console.error('GitHub API error:', error);
        }
    }

    /**
     * Extract repository info from current URL
     */
    getRepositoryInfo() {
        // Check if we're on GitHub Pages
        const hostname = window.location.hostname;
        if (hostname.includes('github.io')) {
            // Extract from GitHub Pages URL: username.github.io/repository-name
            const pathParts = window.location.pathname.split('/').filter(p => p);
            if (pathParts.length > 0) {
                return {
                    owner: hostname.split('.')[0],
                    repo: pathParts[0]
                };
            }
        }
        
        // Fallback: try to extract from referrer or assume defaults
        return {
            owner: 'litlfred',
            repo: 'notebooks'
        };
    }

    /**
     * Generate a readable title from filename
     */
    generateTitleFromFilename(filename) {
        return filename
            .replace(/\.(ipynb|jsonld|json)$/, '')
            .replace(/[-_]/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Update the notebook list in UI
     */
    updateNotebookList() {
        const notebookList = document.getElementById('notebook-items');
        if (!notebookList) return;

        const html = this.availableNotebooks.map(notebook => {
            const icon = this.getNotebookIcon(notebook.type);
            const modifiedText = notebook.modified.includes('T') ? 
                new Date(notebook.modified).toLocaleDateString() : 
                notebook.modified;
            
            return `
                <div class="notebook-item" onclick="notebookLoader.loadNotebook('${notebook.filename}')">
                    <div class="notebook-header">
                        <span class="notebook-icon">${icon}</span>
                        <div class="notebook-title">${notebook.title}</div>
                        <span class="notebook-type">${notebook.type.toUpperCase()}</span>
                    </div>
                    <div class="notebook-description">${notebook.description}</div>
                    <div class="notebook-meta">
                        <span class="notebook-modified">Modified: ${modifiedText}</span>
                        ${notebook.github_url ? `<a href="${notebook.github_url}" target="_blank" class="github-link">View on GitHub</a>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        notebookList.innerHTML = html || '<div class="no-notebooks">No notebooks available</div>';
    }

    /**
     * Get icon for notebook type
     */
    getNotebookIcon(type) {
        const icons = {
            'ipynb': '📓',
            'jsonld': '🔗', 
            'json': '📄'
        };
        return icons[type] || '📄';
    }

    /**
     * Handle file selection for loading
     */
    openFileDialog() {
        this.fileInput.click();
    }

    /**
     * Handle file load from input
     */
    async handleFileLoad(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const content = await this.readFileAsText(file);
            
            // Check if it's a Jupyter notebook
            if (file.name.endsWith('.ipynb')) {
                await this.handleJupyterNotebook(content, file.name);
            } else {
                // Handle as JSON-LD notebook
                const notebook = JSON.parse(content);
                await this.loadNotebookData(notebook);
            }
            
            this.boardApp.updateStatus(`Loaded notebook: ${file.name}`, 'success');
        } catch (error) {
            console.error('Failed to load notebook file:', error);
            this.boardApp.updateStatus(`Failed to load notebook: ${error.message}`, 'error');
        }
    }

    /**
     * Handle drag over event
     */
    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }

    /**
     * Handle file drop
     */
    async handleDrop(event) {
        event.preventDefault();
        const files = Array.from(event.dataTransfer.files);
        const jsonldFile = files.find(f => f.name.endsWith('.jsonld') || f.name.endsWith('.json'));
        
        if (jsonldFile) {
            try {
                const content = await this.readFileAsText(jsonldFile);
                const notebook = JSON.parse(content);
                await this.loadNotebookData(notebook);
                this.boardApp.updateStatus(`Loaded notebook: ${jsonldFile.name}`, 'success');
            } catch (error) {
                console.error('Failed to load dropped notebook:', error);
                this.boardApp.updateStatus(`Failed to load notebook: ${error.message}`, 'error');
            }
        }
    }

    /**
     * Read file as text
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    /**
     * Load notebook from notebooks/ directory
     */
    async loadNotebook(filename) {
        try {
            const response = await fetch(`../notebooks/${filename}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch notebook: ${response.statusText}`);
            }
            
            const content = await response.text();
            
            // Check if it's a Jupyter notebook
            if (filename.endsWith('.ipynb')) {
                await this.handleJupyterNotebook(content, filename);
            } else {
                // Handle as JSON-LD notebook
                const notebook = JSON.parse(content);
                await this.loadNotebookData(notebook);
            }
            
            this.boardApp.updateStatus(`Loaded notebook: ${filename}`, 'success');
        } catch (error) {
            console.error('Failed to load notebook:', error);
            this.boardApp.updateStatus(`Failed to load notebook: ${error.message}`, 'error');
        }
    }

    /**
     * Load notebook data into the board
     */
    async loadNotebookData(notebook) {
        // Clear current board
        this.boardApp.clearBoard();

        // Set notebook metadata
        if (notebook['dct:title']) {
            document.title = `Mathematical Workspace - ${notebook['dct:title']}`;
        }
        
        // Process notebook libraries for UI display
        if (notebook['notebook:libraries']) {
            this.processNotebookLibraries(notebook['notebook:libraries']);
        }

        // Load widgets from graph
        const graph = notebook['@graph'] || [];
        const widgets = graph.filter(item => 
            item['@type'] && item['@type'].some(type => type.includes(':widget'))
        );

        // Load connections
        const connections = graph.filter(item =>
            item['@type'] && item['@type'].includes('notebook:Connection')
        );

        // Create widgets
        for (const widgetData of widgets) {
            await this.createWidgetFromData(widgetData);
        }

        // Create connections
        for (const connectionData of connections) {
            this.createConnectionFromData(connectionData);
        }

        // Set canvas layout if specified
        if (notebook['notebook:layout']) {
            this.applyNotebookLayout(notebook['notebook:layout']);
        }

        this.boardApp.saveBoardToStorage();
    }
    
    /**
     * Process notebook libraries for display enhancement
     */
    processNotebookLibraries(libraries) {
        // Store library information for enhanced display
        this.notebookLibraries = libraries;
        
        // Update the board app with library information
        if (this.boardApp && typeof this.boardApp.updateLibraryDisplay === 'function') {
            this.boardApp.updateLibraryDisplay(libraries);
        }
        
        console.log('Processed notebook libraries:', libraries);
    }

    /**
     * Create widget from JSON-LD data
     */
    async createWidgetFromData(widgetData) {
        // Extract widget type from @type array
        const typeArray = Array.isArray(widgetData['@type']) ? widgetData['@type'] : [widgetData['@type']];
        const widgetTypeEntry = typeArray.find(type => type.includes(':widget') || type.includes(':'));
        
        // Map JSON-LD types to widget types
        let widgetType = 'sticky-note'; // default
        if (widgetTypeEntry) {
            if (widgetTypeEntry.includes('pqt:widget')) {
                widgetType = 'pq-torus';
            } else if (widgetTypeEntry.includes('weier:two-panel')) {
                widgetType = 'pq-torus.weierstrass.two-panel';
            } else if (widgetTypeEntry.includes('weier:five-panel')) {
                widgetType = 'pq-torus.weierstrass.five-panel';
            } else if (widgetTypeEntry.includes('weier:trajectories')) {
                widgetType = 'pq-torus.weierstrass.trajectories';
            } else if (widgetTypeEntry.includes('sticky:widget')) {
                widgetType = 'sticky-note';
            } else if (widgetTypeEntry.includes('jupyter:markdown-cell')) {
                widgetType = 'jupyter-markdown-cell';
            } else if (widgetTypeEntry.includes('jupyter:code-cell')) {
                widgetType = 'jupyter-code-cell';
            }
        }

        // Extract position and size
        const position = widgetData.layout?.position || widgetData['widget:position'] || { x: 100, y: 100 };
        const size = widgetData.layout?.size || widgetData['widget:size'] || { width: 300, height: 250 };

        // Extract configuration
        const config = widgetData.input || widgetData['prov:value'] || {};
        
        // Create JSON-LD schema from widget data for widget initialization
        const jsonldSchema = {
            '@id': widgetData['@id'],
            '@type': widgetData['@type'],
            'dct:conformsTo': widgetData['dct:conformsTo'],
            'input': widgetData.input || {},
            'output': widgetData.output || {}
        };

        // Create widget with JSON-LD schema
        const widget = this.boardApp.createWidget(widgetType, position.x, position.y, config, jsonldSchema);
        
        if (widget) {
            // Update widget dimensions if specified
            if (size.width && size.height) {
                widget.width = size.width;
                widget.height = size.height;
                const widgetEl = document.querySelector(`[data-widget-id="${widget.id}"]`);
                if (widgetEl) {
                    widgetEl.style.width = `${size.width}px`;
                    widgetEl.style.height = `${size.height}px`;
                }
            }
        
        if (widget) {
            // Apply configuration from prov:value
            if (widgetData['prov:value']) {
                Object.assign(widget.config, widgetData['prov:value']);
            }

            // Set widget properties
            if (widgetData['widget:title']) {
                widget.title = widgetData['widget:title'];
            }

            // Set size
            widget.width = size.width;
            widget.height = size.height;

            // Apply widget note if present
            if (widgetData['widget:note']) {
                widget.note = widgetData['widget:note'];
            }

            // For sticky notes, apply theme
            if (widgetType === 'sticky-note' && widgetData['widget:theme']) {
                widget.stickyTheme = widgetData['widget:theme'];
            }

            // Update widget display
            this.boardApp.updateWidgetDisplay(widget);
        }

        return widget;
    }

    /**
     * Create connection from JSON-LD data
     */
    createConnectionFromData(connectionData) {
        const sourceId = connectionData['notebook:source'];
        const targetId = connectionData['notebook:target'];
        
        // Find widgets by URN (simplified mapping)
        const sourceWidget = Array.from(this.boardApp.widgets.values())
            .find(w => sourceId.includes(w.type) || sourceId.includes(w.id));
        const targetWidget = Array.from(this.boardApp.widgets.values())
            .find(w => targetId.includes(w.type) || targetId.includes(w.id));

        if (sourceWidget && targetWidget) {
            const dataFlow = connectionData['notebook:dataFlow'];
            this.boardApp.connectWidgets(
                sourceWidget.id, 
                targetWidget.id, 
                dataFlow.sourceOutput, 
                dataFlow.targetInput
            );
        }
    }

    /**
     * Apply notebook layout settings
     */
    applyNotebookLayout(layout) {
        if (layout.grid_size) {
            this.boardApp.gridSize = layout.grid_size;
        }
        
        if (layout.canvas_size) {
            const boardContent = document.getElementById('board-content');
            if (boardContent) {
                boardContent.style.width = `${layout.canvas_size.width}px`;
                boardContent.style.height = `${layout.canvas_size.height}px`;
            }
        }
    }

    /**
     * Save current board as JSON-LD notebook
     */
    saveNotebook(filename) {
        const notebook = this.generateNotebookData();
        const content = JSON.stringify(notebook, null, 2);
        
        // Create download link
        const blob = new Blob([content], { type: 'application/ld+json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'mathematical-notebook.jsonld';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.boardApp.updateStatus(`Notebook saved: ${a.download}`, 'success');
    }

    /**
     * Generate JSON-LD notebook data from current board state
     */
    generateNotebookData() {
        const widgets = Array.from(this.boardApp.widgets.values());
        const timestamp = new Date().toISOString();
        
        const notebook = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
            ],
            "@id": `urn:notebook:${Date.now()}`,
            "@type": ["prov:Entity", "notebook:Notebook"],
            "dct:title": "Mathematical Workspace",
            "dct:description": "Interactive computational notebook with widget workflow",
            "dct:created": timestamp,
            "dct:modified": timestamp,
            "@graph": []
        };

        // Add widgets to graph
        widgets.forEach(widget => {
            const widgetData = {
                "@id": `urn:widget:${widget.id}`,
                "@type": ["prov:Entity", this.getWidgetJsonLdType(widget.type)],
                "widget:instanceId": widget.id,
                "widget:position": { x: widget.x, y: widget.y },
                "widget:size": { width: widget.width, height: widget.height },
                "widget:title": widget.title,
                "prov:value": widget.config
            };

            if (widget.note) {
                widgetData['widget:note'] = widget.note;
            }

            if (widget.type === 'sticky-note' && widget.stickyTheme) {
                widgetData['widget:theme'] = widget.stickyTheme;
            }

            notebook["@graph"].push(widgetData);
        });

        // Add connections
        this.boardApp.connections.forEach((connections, sourceId) => {
            connections.forEach(conn => {
                notebook["@graph"].push({
                    "@id": `urn:connection:${sourceId}-${conn.target}`,
                    "@type": ["prov:Entity", "notebook:Connection"],
                    "notebook:source": `urn:widget:${sourceId}`,
                    "notebook:target": `urn:widget:${conn.target}`,
                    "notebook:dataFlow": {
                        "sourceOutput": conn.output_path,
                        "targetInput": conn.input_path
                    }
                });
            });
        });

        return notebook;
    }

    /**
     * Map widget type to JSON-LD type
     */
    getWidgetJsonLdType(widgetType) {
        const typeMap = {
            'sticky-note': 'sticky:widget',
            'pq-torus': 'pqt:widget',
            'pq-torus.weierstrass.two-panel': 'weier:two-panel',
            'pq-torus.weierstrass.five-panel': 'weier:five-panel',
            'pq-torus.weierstrass.trajectories': 'weier:trajectories',
            'pq-torus.weierstrass.contours': 'weier:contours'
        };
        
        return typeMap[widgetType] || 'widget:generic';
    }

    /**
     * Handle Jupyter notebook import
     */
    async handleJupyterNotebook(content, filename) {
        try {
            const jupyterData = JSON.parse(content);
            
            // Validate notebook format
            if (!this.validateJupyterNotebook(jupyterData)) {
                throw new Error('Invalid Jupyter notebook format');
            }

            // Show import options dialog
            const importMode = await this.showJupyterImportDialog(jupyterData, filename);
            if (!importMode) return; // User cancelled

            // Convert to widget format
            const widgetNotebook = this.convertJupyterToWidgets(jupyterData, importMode, filename);
            
            // Load into board
            await this.loadNotebookData(widgetNotebook);
            
            this.boardApp.updateStatus(`Imported Jupyter notebook: ${filename}`, 'success');
        } catch (error) {
            console.error('Jupyter import error:', error);
            this.boardApp.updateStatus(`Failed to import Jupyter notebook: ${error.message}`, 'error');
        }
    }

    /**
     * Validate Jupyter notebook format
     */
    validateJupyterNotebook(data) {
        const required = ['cells', 'metadata', 'nbformat'];
        for (let field of required) {
            if (!(field in data)) return false;
        }
        
        if (!Array.isArray(data.cells)) return false;
        if (data.nbformat < 3) return false;
        
        return true;
    }

    /**
     * Show import options dialog for Jupyter notebooks
     */
    async showJupyterImportDialog(jupyterData, filename) {
        return new Promise((resolve) => {
            const cells = jupyterData.cells || [];
            const metadata = jupyterData.metadata || {};
            
            const cellCounts = cells.reduce((acc, cell) => {
                acc[cell.cell_type] = (acc[cell.cell_type] || 0) + 1;
                return acc;
            }, {});

            const dialogHtml = `
                <div class="jupyter-import-dialog">
                    <h3>Import Jupyter Notebook</h3>
                    <div class="notebook-info">
                        <p><strong>File:</strong> ${filename}</p>
                        <p><strong>Format:</strong> nbformat ${jupyterData.nbformat}.${jupyterData.nbformat_minor || 0}</p>
                        <p><strong>Language:</strong> ${metadata.language_info?.name || 'Unknown'}</p>
                        <p><strong>Kernel:</strong> ${metadata.kernelspec?.display_name || 'Unknown'}</p>
                        <p><strong>Total Cells:</strong> ${cells.length}</p>
                        <div class="cell-breakdown">
                            ${Object.entries(cellCounts).map(([type, count]) => 
                                `<span class="cell-count">${count} ${type}</span>`
                            ).join(' ')}
                        </div>
                    </div>
                    <div class="import-options">
                        <label><input type="radio" name="import-mode" value="import" checked> 
                            Import (editable copy)</label>
                        <label><input type="radio" name="import-mode" value="link"> 
                            Link (read-only reference)</label>
                    </div>
                    <div class="dialog-buttons">
                        <button id="jupyter-import-btn">Import</button>
                        <button id="jupyter-cancel-btn">Cancel</button>
                    </div>
                </div>
            `;

            // Create dialog overlay
            const overlay = document.createElement('div');
            overlay.className = 'dialog-overlay';
            overlay.innerHTML = dialogHtml;
            document.body.appendChild(overlay);

            // Handle buttons
            overlay.querySelector('#jupyter-import-btn').onclick = () => {
                const mode = overlay.querySelector('input[name="import-mode"]:checked').value;
                document.body.removeChild(overlay);
                resolve(mode);
            };

            overlay.querySelector('#jupyter-cancel-btn').onclick = () => {
                document.body.removeChild(overlay);
                resolve(null);
            };
        });
    }

    /**
     * Convert Jupyter notebook to widget format
     */
    convertJupyterToWidgets(jupyterData, importMode, filename) {
        const cells = jupyterData.cells || [];
        const metadata = jupyterData.metadata || {};
        
        const widgets = [];
        const connections = [];
        let previousWidgetId = null;

        cells.forEach((cell, index) => {
            if (!['markdown', 'code'].includes(cell.cell_type)) {
                return; // Skip unsupported cell types
            }

            const widget = this.createJupyterCellWidget(cell, index, importMode);
            widgets.push(widget);

            // Create sequential arrow to previous cell
            if (previousWidgetId) {
                const connection = this.createSequentialConnection(previousWidgetId, widget['@id'], index);
                connections.append(connection);
            }

            previousWidgetId = widget['@id'];
        });

        // Create notebook JSON-LD structure
        return {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/libraries/core/common/context.jsonld"
            ],
            "@id": `urn:notebook:jupyter-${Date.now()}`,
            "@type": ["prov:Entity", "jupyter:notebook"],
            "dct:title": metadata.title || `Imported: ${filename}`,
            "dct:description": `Jupyter notebook imported in ${importMode} mode with ${cells.length} cells`,
            "jupyter:source_filename": filename,
            "jupyter:import_mode": importMode,
            "jupyter:nbformat": `${jupyterData.nbformat}.${jupyterData.nbformat_minor || 0}`,
            "jupyter:language": metadata.language_info?.name || 'unknown',
            "jupyter:kernel": metadata.kernelspec?.display_name || 'unknown',
            "prov:generatedAtTime": new Date().toISOString(),
            "@graph": [...widgets, ...connections]
        };
    }

    /**
     * Create widget from Jupyter cell
     */
    createJupyterCellWidget(cell, index, importMode) {
        const cellId = `urn:widget:jupyter-${cell.cell_type}-cell-${index}`;
        
        // Extract cell content
        let content = '';
        if (Array.isArray(cell.source)) {
            content = cell.source.join('');
        } else {
            content = cell.source || '';
        }

        const baseWidget = {
            "@id": cellId,
            "@type": ["prov:Entity", `jupyter:${cell.cell_type}-cell`, "widget:instance"],
            "jupyter:cell_index": index,
            "jupyter:cell_type": cell.cell_type,
            "jupyter:import_mode": importMode,
            "widget:position": {
                "x": 100 + (index % 3) * 350,
                "y": 100 + Math.floor(index / 3) * 300
            },
            "widget:size": {
                "width": 320,
                "height": 250
            },
            "prov:generatedAtTime": new Date().toISOString()
        };

        if (cell.cell_type === 'markdown') {
            return {
                ...baseWidget,
                "widget:type": "jupyter-markdown-cell",
                "input": {
                    "@id": `${cellId}:input`,
                    "@type": ["prov:Entity", "jupyter:markdown-input"],
                    "content": content,
                    "show_note": true,
                    "cell_metadata": cell.metadata || {},
                    "attachments": cell.attachments || {},
                    "cell_index": index
                }
            };
        } else if (cell.cell_type === 'code') {
            return {
                ...baseWidget,
                "widget:type": "jupyter-code-cell",
                "input": {
                    "@id": `${cellId}:input`,
                    "@type": ["prov:Entity", "jupyter:code-input"],
                    "code": content,
                    "execute_immediately": false,
                    "cell_metadata": cell.metadata || {},
                    "outputs": cell.outputs || [],
                    "execution_count": cell.execution_count,
                    "cell_index": index
                }
            };
        }
    }

    /**
     * Create sequential connection between cells
     */
    createSequentialConnection(sourceId, targetId, targetIndex) {
        return {
            "@id": `urn:connection:sequential-${targetIndex}`,
            "@type": ["prov:Entity", "workflow:Connection", "jupyter:sequential-arrow"],
            "workflow:connection_type": "sequential_flow",
            "jupyter:connection_reason": "Sequential execution order in notebook",
            "source": {
                "widget": sourceId,
                "output": `${sourceId}:output`
            },
            "target": {
                "widget": targetId,
                "input": `${targetId}:input`
            },
            "visual": {
                "arrow_style": "sequential",
                "color": "#4A90E2",
                "label": `Cell ${targetIndex - 1} → ${targetIndex}`
            },
            "prov:generatedAtTime": new Date().toISOString()
        };
    }

    /**
     * Import Jupyter notebook from URL
     */
    async importFromUrl(url, importMode = 'link') {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            await this.handleJupyterNotebook(content, url.split('/').pop() || 'notebook.ipynb');
            
        } catch (error) {
            console.error('URL import error:', error);
            this.boardApp.updateStatus(`Failed to import from URL: ${error.message}`, 'error');
        }
    }

    /**
     * Map widget type to JSON-LD type
     */
    getWidgetJsonLdType(widgetType) {
        const typeMap = {
            'sticky-note': 'sticky:widget',
            'pq-torus': 'pqt:widget',
            'pq-torus.weierstrass.two-panel': 'weier:two-panel',
            'pq-torus.weierstrass.five-panel': 'weier:five-panel',
            'pq-torus.weierstrass.trajectories': 'weier:trajectories',
            'pq-torus.weierstrass.contours': 'weier:contours',
            'jupyter-markdown-cell': 'jupyter:markdown-cell',
            'jupyter-code-cell': 'jupyter:code-cell'
        };
        
        return typeMap[widgetType] || 'widget:generic';
    }
}

// Global notebook loader instance
let notebookLoader;

// Notebook management functions
function loadNotebookFile() {
    if (notebookLoader) {
        notebookLoader.openFileDialog();
    }
}

function saveNotebookFile() {
    if (notebookLoader) {
        const filename = prompt('Enter filename for notebook:', 'my-notebook.jsonld');
        if (filename) {
            notebookLoader.saveNotebook(filename);
        }
    }
}

function loadExampleNotebook() {
    if (notebookLoader) {
        notebookLoader.loadNotebook('example-weierstrass-workflow.jsonld');
    }
}