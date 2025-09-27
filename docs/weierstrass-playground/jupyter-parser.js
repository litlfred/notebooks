/**
 * Jupyter Notebook Parser for Mathematical Workspace
 * Converts .ipynb files to widget instances with proper schema compliance
 * Supports nbformat specification with cell attachments and outputs
 */

class JupyterParser {
    constructor(boardApp) {
        this.boardApp = boardApp;
        this.cellSpacing = 280; // Vertical spacing between cells
        this.startPosition = { x: 100, y: 100 };
    }

    /**
     * Parse Jupyter notebook (.ipynb) file and convert to widgets
     * @param {Object} notebookData - Parsed JSON from .ipynb file
     * @returns {Array} Array of widget configurations
     */
    async parseNotebook(notebookData) {
        // Validate nbformat
        if (!this.validateNbformat(notebookData)) {
            throw new Error('Invalid Jupyter notebook format');
        }

        const widgets = [];
        const connections = [];
        const cells = notebookData.cells || [];

        // Process each cell
        for (let i = 0; i < cells.length; i++) {
            const cell = cells[i];
            const widget = await this.createWidgetFromCell(cell, i);
            
            if (widget) {
                widgets.push(widget);
                
                // Create sequential connection to previous cell (if not first)
                if (i > 0) {
                    connections.push({
                        source: widgets[i-1].id,
                        target: widget.id,
                        type: 'sequential',
                        label: `Cell ${i} → Cell ${i+1}`
                    });
                }
            }
        }

        return { widgets, connections, metadata: this.extractNotebookMetadata(notebookData) };
    }

    /**
     * Validate notebook format according to nbformat specification
     */
    validateNbformat(notebookData) {
        if (!notebookData || typeof notebookData !== 'object') {
            return false;
        }

        // Check required fields
        const requiredFields = ['cells', 'metadata', 'nbformat'];
        for (const field of requiredFields) {
            if (!(field in notebookData)) {
                console.warn(`Missing required field: ${field}`);
                return false;
            }
        }

        // Check nbformat version (support v4+)
        if (notebookData.nbformat < 4) {
            console.warn(`Unsupported nbformat version: ${notebookData.nbformat}`);
            return false;
        }

        return true;
    }

    /**
     * Create widget from Jupyter cell
     */
    async createWidgetFromCell(cell, index) {
        const position = {
            x: this.startPosition.x,
            y: this.startPosition.y + (index * this.cellSpacing)
        };

        switch (cell.cell_type) {
            case 'markdown':
                return this.createMarkdownWidget(cell, position, index);
            case 'code':
                return this.createCodeWidget(cell, position, index);
            case 'raw':
                return this.createRawWidget(cell, position, index);
            default:
                console.warn(`Unknown cell type: ${cell.cell_type}`);
                return null;
        }
    }

    /**
     * Create markdown cell widget (extends sticky-note)
     */
    createMarkdownWidget(cell, position, index) {
        const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
        
        const widget = this.boardApp.createWidget('jupyter-markdown-cell', position.x, position.y);
        if (!widget) return null;

        // Configure widget
        widget.config = {
            content: source,
            render_latex: true,
            variables: {}
        };

        // Add Jupyter metadata
        widget.jupyter = {
            cell_type: 'markdown',
            execution_count: cell.execution_count || null,
            metadata: cell.metadata || {},
            id: cell.id || `cell-${index}`,
            attachments: cell.attachments || {}
        };

        widget.title = `Markdown Cell ${index + 1}`;
        widget.height = Math.max(200, Math.min(400, source.length * 0.5 + 150));

        return widget;
    }

    /**
     * Create code cell widget
     */
    createCodeWidget(cell, position, index) {
        const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
        
        const widget = this.boardApp.createWidget('jupyter-code-cell', position.x, position.y);
        if (!widget) return null;

        // Configure input
        widget.config = {
            input: {
                source: source,
                language: this.detectLanguage(cell.metadata),
                execution_timeout: 30
            },
            output: {
                execution_count: cell.execution_count,
                outputs: this.processOutputs(cell.outputs || [])
            }
        };

        // Add Jupyter metadata
        widget.jupyter = {
            cell_type: 'code',
            metadata: cell.metadata || {},
            id: cell.id || `cell-${index}`
        };

        widget.title = `Code Cell ${index + 1}`;
        widget.height = Math.max(300, Math.min(500, source.length * 0.3 + 200));

        return widget;
    }

    /**
     * Create raw cell widget
     */
    createRawWidget(cell, position, index) {
        const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
        
        const widget = this.boardApp.createWidget('jupyter-raw-cell', position.x, position.y);
        if (!widget) return null;

        // Configure widget
        widget.config = {
            input: {
                source: source,
                format: cell.metadata?.format || 'text'
            },
            output: {
                rendered_content: source,
                format_applied: cell.metadata?.format || 'text'
            }
        };

        // Add Jupyter metadata
        widget.jupyter = {
            cell_type: 'raw',
            metadata: cell.metadata || {},
            id: cell.id || `cell-${index}`
        };

        widget.title = `Raw Cell ${index + 1}`;
        widget.height = Math.max(150, Math.min(300, source.length * 0.4 + 100));

        return widget;
    }

    /**
     * Process Jupyter cell outputs according to nbformat
     */
    processOutputs(outputs) {
        return outputs.map(output => {
            const processed = {
                output_type: output.output_type
            };

            switch (output.output_type) {
                case 'stream':
                    processed.name = output.name;
                    processed.text = output.text;
                    break;
                
                case 'display_data':
                case 'execute_result':
                    processed.data = output.data || {};
                    processed.metadata = output.metadata || {};
                    if (output.execution_count !== undefined) {
                        processed.execution_count = output.execution_count;
                    }
                    break;
                
                case 'error':
                    processed.ename = output.ename;
                    processed.evalue = output.evalue;
                    processed.traceback = output.traceback || [];
                    break;
            }

            return processed;
        });
    }

    /**
     * Detect programming language from cell metadata
     */
    detectLanguage(metadata) {
        if (metadata?.kernelspec?.language) {
            return metadata.kernelspec.language;
        }
        
        if (metadata?.language_info?.name) {
            return metadata.language_info.name;
        }

        return 'python'; // default
    }

    /**
     * Extract notebook-level metadata
     */
    extractNotebookMetadata(notebookData) {
        const metadata = notebookData.metadata || {};
        
        return {
            title: metadata.title || 'Imported Jupyter Notebook',
            authors: metadata.authors || [],
            created: new Date().toISOString(),
            nbformat: notebookData.nbformat,
            nbformat_minor: notebookData.nbformat_minor,
            kernelspec: metadata.kernelspec || {},
            language_info: metadata.language_info || {},
            original_metadata: metadata
        };
    }

    /**
     * Load Jupyter notebook from file
     */
    async loadJupyterNotebook(file) {
        try {
            const content = await this.readFileAsText(file);
            const notebookData = JSON.parse(content);
            
            const { widgets, connections, metadata } = await this.parseNotebook(notebookData);
            
            // Clear current board
            this.boardApp.clearBoard();
            
            // Set notebook title
            if (metadata.title) {
                document.title = `Mathematical Workspace - ${metadata.title}`;
            }
            
            // Create widgets
            const createdWidgets = [];
            for (const widgetConfig of widgets) {
                createdWidgets.push(widgetConfig);
            }
            
            // Create sequential connections
            for (const connection of connections) {
                this.boardApp.connectWidgets(
                    connection.source,
                    connection.target,
                    'sequential_output',
                    'sequential_input'
                );
            }
            
            // Save to storage
            this.boardApp.saveBoardToStorage();
            
            return {
                success: true,
                widgets: createdWidgets.length,
                metadata
            };
            
        } catch (error) {
            console.error('Failed to load Jupyter notebook:', error);
            throw new Error(`Failed to parse Jupyter notebook: ${error.message}`);
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
     * Generate JSON-LD export from imported Jupyter notebook
     */
    exportToJsonLD(widgets, metadata) {
        const timestamp = new Date().toISOString();
        
        const notebook = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
            ],
            "@id": `urn:notebook:jupyter-import:${Date.now()}`,
            "@type": ["prov:Entity", "notebook:Notebook", "jupyter:ImportedNotebook"],
            "dct:title": metadata.title,
            "dct:description": "Jupyter notebook imported to mathematical workspace",
            "dct:created": timestamp,
            "dct:source": "jupyter-notebook",
            "jupyter:nbformat": metadata.nbformat,
            "jupyter:kernelspec": metadata.kernelspec,
            "@graph": []
        };

        // Add widgets to graph
        widgets.forEach(widget => {
            const widgetData = {
                "@id": `urn:widget:jupyter:${widget.id}`,
                "@type": ["prov:Entity", this.getJupyterWidgetJsonLdType(widget.jupyter.cell_type)],
                "widget:instanceId": widget.id,
                "widget:position": { x: widget.x, y: widget.y },
                "widget:size": { width: widget.width, height: widget.height },
                "widget:title": widget.title,
                "jupyter:cellType": widget.jupyter.cell_type,
                "jupyter:metadata": widget.jupyter.metadata,
                "prov:value": widget.config
            };

            notebook["@graph"].push(widgetData);
        });

        return notebook;
    }

    /**
     * Map Jupyter cell type to JSON-LD type
     */
    getJupyterWidgetJsonLdType(cellType) {
        const typeMap = {
            'markdown': 'jupyter:markdown-cell',
            'code': 'jupyter:code-cell',
            'raw': 'jupyter:raw-cell'
        };
        
        return typeMap[cellType] || 'jupyter:unknown-cell';
    }
}

// Export for use in other modules
window.JupyterParser = JupyterParser;