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
        fileInput.accept = '.jsonld,.json';
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
            // In a real implementation, this would fetch from a server endpoint
            // For now, we'll use a static list of known notebooks
            this.availableNotebooks = [
                {
                    filename: 'example-weierstrass-workflow.jsonld',
                    title: 'Weierstrass Function Analysis with p=5, q=7',
                    description: 'Complete mathematical workflow demonstrating PQ-Torus lattice parameters',
                    modified: '2024-01-15T12:15:00Z'
                }
            ];
            
            this.updateNotebookList();
        } catch (error) {
            console.error('Failed to load available notebooks:', error);
        }
    }

    /**
     * Update the notebook list in UI
     */
    updateNotebookList() {
        const notebookList = document.getElementById('notebook-list');
        if (!notebookList) return;

        const html = this.availableNotebooks.map(notebook => `
            <div class="notebook-item" onclick="notebookLoader.loadNotebook('${notebook.filename}')">
                <div class="notebook-title">${notebook.title}</div>
                <div class="notebook-description">${notebook.description}</div>
                <div class="notebook-modified">Modified: ${new Date(notebook.modified).toLocaleDateString()}</div>
            </div>
        `).join('');

        notebookList.innerHTML = html || '<div class="no-notebooks">No notebooks available</div>';
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
            const notebook = JSON.parse(content);
            await this.loadNotebookData(notebook);
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
            
            const notebook = await response.json();
            await this.loadNotebookData(notebook);
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
            }
        }

        // Extract position and size
        const position = widgetData['widget:position'] || { x: 100, y: 100 };
        const size = widgetData['widget:size'] || { width: 300, height: 250 };

        // Create widget
        const widget = this.boardApp.createWidget(widgetType, position.x, position.y);
        
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
    async saveNotebook(filename) {
        try {
            const notebook = await this.generateNotebookData();
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
        } catch (error) {
            console.error('Failed to save notebook:', error);
            this.boardApp.updateStatus(`Failed to save notebook: ${error.message}`, 'error');
        }
    }

    /**
     * Generate JSON-LD notebook data from current board state
     */
    async generateNotebookData() {
        const widgets = Array.from(this.boardApp.widgets.values());
        const timestamp = new Date().toISOString();
        
        // Ensure deployment utils are initialized
        if (!window.deploymentUtils.initialized) {
            await window.deploymentUtils.initialize();
        }
        
        const notebookId = Date.now();
        const notebook = {
            "@context": window.deploymentUtils.getNotebookContext(),
            "@id": window.deploymentUtils.getNotebookUrn(notebookId),
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
                "@id": window.deploymentUtils.getWidgetUrn(widget.id),
                "@type": ["prov:Entity", this.getWidgetJsonLdType(widget.type)],
                "dct:conformsTo": window.deploymentUtils.getSchemaConformanceUrl(
                    this.getWidgetSchemaName(widget.type), 
                    'widget'
                ),
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
                    "@id": window.deploymentUtils.getConnectionUrn(sourceId, conn.target),
                    "@type": ["prov:Entity", "notebook:Connection"],
                    "notebook:source": window.deploymentUtils.getWidgetUrn(sourceId),
                    "notebook:target": window.deploymentUtils.getWidgetUrn(conn.target),
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
     * Map widget type to schema name for URL generation
     */
    getWidgetSchemaName(widgetType) {
        const schemaMap = {
            'sticky-note': 'sticky-note',
            'pq-torus': 'pq-torus',
            'pq-torus.weierstrass.two-panel': 'pq-torus/weierstrass/two-panel',
            'pq-torus.weierstrass.five-panel': 'pq-torus/weierstrass/five-panel',
            'pq-torus.weierstrass.trajectories': 'pq-torus/weierstrass/trajectories',
            'pq-torus.weierstrass.contours': 'pq-torus/weierstrass/contours'
        };
        
        return schemaMap[widgetType] || 'common';
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
}

// Global notebook loader instance
let notebookLoader;

// Notebook management functions
function loadNotebookFile() {
    if (notebookLoader) {
        notebookLoader.openFileDialog();
    }
}

async function saveNotebookFile() {
    if (notebookLoader) {
        const filename = prompt('Enter filename for notebook:', 'my-notebook.jsonld');
        if (filename) {
            await notebookLoader.saveNotebook(filename);
        }
    }
}

function loadExampleNotebook() {
    if (notebookLoader) {
        notebookLoader.loadNotebook('example-weierstrass-workflow.jsonld');
    }
}