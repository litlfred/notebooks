/**
 * Mathematical Board - Advanced Miro-like Interactive Workspace
 * Handles JSON schema-based widgets, execution, and connections
 */

class MathematicalBoard {
    constructor() {
        this.widgets = new Map();
        this.widgetSchemas = null;
        this.widgetGraph = new WidgetGraph();
        this.selectedWidget = null;
        this.dragOffset = { x: 0, y: 0 };
        this.widgetCounter = 0;
        this.isLibraryOpen = true;
        this.gridEnabled = true;
        this.connections = new Map(); // widget connections for data flow
        
        this.initializeBoard();
        this.setupEventListeners();
        this.initializeUserPreferences();
        this.loadWidgetSchemas();
    }

    /**
     * Load widget schemas from JSON file
     */
    async loadWidgetSchemas() {
        try {
            const response = await fetch('widget-schemas.json');
            this.widgetSchemas = await response.json();
            console.log('Widget schemas loaded:', this.widgetSchemas);
            
            // Update widget library with schema information
            this.updateWidgetLibraryFromSchemas();
            
        } catch (error) {
            console.error('Failed to load widget schemas:', error);
            this.widgetSchemas = { 'widget-schemas': {} };
        }
    }

    /**
     * Update widget library display with schema-based widgets
     */
    updateWidgetLibraryFromSchemas() {
        if (!this.widgetSchemas || !this.widgetSchemas['widget-schemas']) return;

        const schemas = this.widgetSchemas['widget-schemas'];
        const categories = {};
        
        // Group widgets by category
        Object.values(schemas).forEach(schema => {
            const category = schema.category || 'other';
            if (!categories[category]) categories[category] = [];
            categories[category].push(schema);
        });

        // Update library display
        const libraryContainer = document.querySelector('.widget-categories');
        if (!libraryContainer) return;

        libraryContainer.innerHTML = '';

        Object.entries(categories).forEach(([categoryName, widgets]) => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'widget-category';
            
            const categoryHeader = document.createElement('h4');
            categoryHeader.innerHTML = `<span class="category-icon">${this.getCategoryIcon(categoryName)}</span> ${this.formatCategoryName(categoryName)}`;
            categoryDiv.appendChild(categoryHeader);
            
            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'widget-items';
            
            widgets.forEach(widget => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'widget-item';
                itemDiv.draggable = true;
                itemDiv.dataset.widgetType = widget.id;
                itemDiv.dataset.widgetSchema = JSON.stringify(widget);
                
                itemDiv.innerHTML = `
                    <span class="widget-icon">${widget.icon}</span>
                    <span>${widget.name}</span>
                `;
                
                itemDiv.addEventListener('dragstart', this.handleWidgetDragStart.bind(this));
                itemDiv.addEventListener('click', this.handleWidgetClick.bind(this));
                
                itemsDiv.appendChild(itemDiv);
            });
            
            categoryDiv.appendChild(itemsDiv);
            libraryContainer.appendChild(categoryDiv);
        });
    }

    getCategoryIcon(category) {
        const icons = {
            'content': '📝',
            'computation': '🐍', 
            'visualization': '∞',
            'data': '📋'
        };
        return icons[category] || '🧩';
    }

    formatCategoryName(category) {
        const names = {
            'content': 'CONTENT',
            'computation': 'COMPUTATION',
            'visualization': 'VISUALIZATION', 
            'data': 'DATA'
        };
        return names[category] || category.toUpperCase();
    }

    /**
     * Initialize the board
     */
    initializeBoard() {
        const boardContent = document.getElementById('board-content');
        
        // Setup drag and drop
        this.setupDragAndDrop();
        
        // Load saved board if exists
        this.loadBoardFromStorage();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Widget library items
        const widgetItems = document.querySelectorAll('.widget-item');
        widgetItems.forEach(item => {
            item.addEventListener('dragstart', this.handleWidgetDragStart.bind(this));
            item.addEventListener('click', this.handleWidgetClick.bind(this));
        });

        // Board content
        const boardContent = document.getElementById('board-content');
        boardContent.addEventListener('click', (e) => {
            if (e.target === boardContent) {
                this.deselectAllWidgets();
            }
        });

        // Control panel toggle
        const panelToggle = document.getElementById('panel-toggle');
        if (panelToggle) {
            panelToggle.addEventListener('click', () => {
                document.getElementById('global-controls').classList.toggle('expanded');
            });
        }

        // Resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        const boardContent = document.getElementById('board-content');
        
        boardContent.addEventListener('dragover', (e) => {
            e.preventDefault();
            boardContent.classList.add('drag-over');
        });

        boardContent.addEventListener('dragleave', (e) => {
            if (!boardContent.contains(e.relatedTarget)) {
                boardContent.classList.remove('drag-over');
            }
        });

        boardContent.addEventListener('drop', (e) => {
            e.preventDefault();
            boardContent.classList.remove('drag-over');
            
            const widgetType = e.dataTransfer.getData('text/widget-type');
            if (widgetType) {
                const rect = boardContent.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.createWidget(widgetType, x, y);
            }
        });
    }

    /**
     * Handle widget drag start
     */
    handleWidgetDragStart(e) {
        const widgetType = e.target.closest('.widget-item').dataset.widgetType;
        e.dataTransfer.setData('text/widget-type', widgetType);
        e.target.closest('.widget-item').classList.add('dragging');
        
        setTimeout(() => {
            e.target.closest('.widget-item').classList.remove('dragging');
        }, 100);
    }

    /**
     * Handle widget click (double-click to add)
     */
    handleWidgetClick(e) {
        const widgetType = e.target.closest('.widget-item').dataset.widgetType;
        
        // Add to center of visible area
        const boardContent = document.getElementById('board-content');
        const rect = boardContent.getBoundingClientRect();
        const x = rect.width / 2;
        const y = rect.height / 2;
        
        this.createWidget(widgetType, x, y);
    }

    /**
     * Create a new widget using JSON schema
     */
    createWidget(type, x, y, customConfig = {}) {
        if (!this.widgetSchemas || !this.widgetSchemas['widget-schemas'][type]) {
            console.error(`Widget schema not found for type: ${type}`);
            return;
        }

        const schema = this.widgetSchemas['widget-schemas'][type];
        const widgetId = `widget-${++this.widgetCounter}`;
        
        // Get default configuration from schema
        const defaultConfig = this.getDefaultConfigFromSchema(schema);
        
        const widget = {
            id: widgetId,
            type: type,
            x: x,
            y: y,
            width: 350,
            height: 250,
            title: schema.name,
            icon: schema.icon,
            description: schema.description,
            config: { ...defaultConfig, ...customConfig },
            schema: schema,
            actions: schema.actions || {},
            connections: {
                inputs: new Map(),
                outputs: new Map()
            },
            lastOutput: null,
            status: 'idle' // idle, running, completed, error
        };

        // Create DOM element
        const element = this.createWidgetElement(widget);
        
        // Add to board
        document.getElementById('board-content').appendChild(element);
        
        // Store widget
        this.widgets.set(widgetId, widget);
        
        // Make draggable
        this.makeDraggable(element);
        
        // Auto-select new widget
        this.selectWidget(widgetId);
        
        // Auto-save
        this.saveBoardToStorage();
        
        console.log(`Created ${type} widget:`, widget);
        return widget;
    }

    /**
     * Extract default configuration from JSON schema
     */
    getDefaultConfigFromSchema(schema) {
        const config = {};
        
        if (schema.input_schema && schema.input_schema.properties) {
            Object.entries(schema.input_schema.properties).forEach(([key, propSchema]) => {
                if ('default' in propSchema) {
                    config[key] = propSchema.default;
                }
            });
        }
        
        return config;
    }

    /**
     * Create widget DOM element with schema-based structure
     */
    createWidgetElement(widget) {
        const element = document.createElement('div');
        element.className = `board-widget widget-${widget.type} status-${widget.status}`;
        element.dataset.widgetId = widget.id;
        element.style.left = `${widget.x}px`;
        element.style.top = `${widget.y}px`;
        element.style.width = `${widget.width}px`;
        element.style.height = `${widget.height}px`;

        // Status indicator
        const statusClass = widget.status === 'running' ? 'fa-spin' : '';
        const statusIcon = this.getStatusIcon(widget.status);

        element.innerHTML = `
            <div class="widget-header">
                <div class="widget-title">
                    <span class="widget-icon">${widget.icon}</span>
                    <span class="widget-name">${widget.title}</span>
                    <span class="widget-status ${statusClass}" title="${widget.status}">
                        ${statusIcon}
                    </span>
                </div>
                <div class="widget-actions">
                    <div class="widget-hamburger-menu">
                        <button class="widget-btn hamburger-toggle" onclick="toggleWidgetMenu('${widget.id}')" title="Actions">
                            ☰
                        </button>
                        <div class="hamburger-dropdown" id="menu-${widget.id}" style="display: none;">
                            ${this.renderActionMenu(widget)}
                        </div>
                    </div>
                    <button class="widget-btn" onclick="editWidget('${widget.id}')" title="Configure">
                        ⚙️
                    </button>
                    <button class="widget-btn" onclick="runWidget('${widget.id}')" title="Execute Default">
                        ▶️
                    </button>
                    <button class="widget-btn" onclick="connectWidget('${widget.id}')" title="Connect">
                        🔗
                    </button>
                    <button class="widget-btn" onclick="deleteWidget('${widget.id}')" title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
            <div class="widget-content" id="content-${widget.id}">
                ${this.renderWidgetContent(widget)}
            </div>
            <div class="widget-connections" id="connections-${widget.id}">
                ${this.renderWidgetConnections(widget)}
            </div>
        `;

        return element;
    }

    /**
     * Get status icon for widget
     */
    getStatusIcon(status) {
        const icons = {
            'idle': '⭕',
            'running': '🔄',
            'completed': '✅',
            'error': '❌'
        };
        return icons[status] || '❓';
    }

    /**
     * Render widget content based on schema and current state
     */
    renderWidgetContent(widget) {
        if (!widget.schema) {
            return '<div class="widget-error">Schema not found</div>';
        }

        // Show configuration preview
        const configPreview = this.renderConfigPreview(widget);
        
        // Show last output if available
        const outputDisplay = widget.lastOutput ? 
            this.renderOutput(widget.lastOutput, widget.schema.output_schema) : 
            '<div class="widget-placeholder">No output yet - click Execute to run</div>';

        return `
            <div class="widget-config-preview">
                ${configPreview}
            </div>
            <div class="widget-output">
                ${outputDisplay}
            </div>
        `;
    }

    /**
     * Render configuration preview
     */
    renderConfigPreview(widget) {
        const config = widget.config;
        const schema = widget.schema.input_schema;
        
        if (!schema || !schema.properties) {
            return '<div class="config-empty">No configuration</div>';
        }

        const configItems = Object.entries(config).slice(0, 3).map(([key, value]) => {
            const shortValue = typeof value === 'string' && value.length > 30 ? 
                value.substring(0, 30) + '...' : 
                JSON.stringify(value);
            return `<div class="config-item"><span class="config-key">${key}:</span> ${shortValue}</div>`;
        }).join('');

        const moreCount = Math.max(0, Object.keys(config).length - 3);
        const moreText = moreCount > 0 ? `<div class="config-more">+${moreCount} more...</div>` : '';

        return `<div class="config-preview">${configItems}${moreText}</div>`;
    }

    /**
     * Render widget output based on schema
     */
    renderOutput(output, outputSchema) {
        if (!output || !output.success) {
            return `<div class="output-error">${output?.error || 'Execution failed'}${output?.action_slug ? ` (Action: ${output.action_slug})` : ''}</div>`;
        }

        // Handle action-specific output formats
        if (output.action_slug && output.output_format) {
            switch (output.output_format) {
                case 'html':
                    if (output.rendered_html) {
                        return `<div class="output-html">${output.rendered_html}</div>`;
                    }
                    break;
                case 'svg':
                    if (output.svg_content) {
                        return `<div class="output-svg">${output.svg_content}</div>`;
                    }
                    break;
                case 'png':
                    if (output.image_data && output.image_data.base64) {
                        return `<img src="${output.image_data.base64}" alt="PNG Output" class="output-plot" width="${output.image_data.width || 200}" height="${output.image_data.height || 100}">`;
                    }
                    break;
                case 'pdf':
                    if (output.pdf_data) {
                        return `<div class="output-pdf">
                            <p><strong>PDF Generated:</strong> ${output.pdf_data.pages} page(s), ${output.pdf_data.size}</p>
                            <a href="${output.pdf_data.download_url}" class="pdf-download-link">📄 Download PDF</a>
                        </div>`;
                    }
                    break;
                case 'markdown':
                    if (output.markdown_content) {
                        return `<div class="output-markdown">${output.markdown_content}</div>`;
                    }
                    break;
            }
        }

        // Handle legacy output types
        if (output.rendered_html) {
            return `<div class="output-html">${output.rendered_html}</div>`;
        }
        
        if (output.plot_data && output.plot_data.image_base64) {
            return `<img src="data:image/png;base64,${output.plot_data.image_base64}" alt="Plot" class="output-plot">`;
        }
        
        if (output.data && output.data.x && output.data.y) {
            return `<div class="output-data">Data: ${output.data.x.length} points generated</div>`;
        }
        
        if (output.stdout) {
            return `<pre class="output-stdout">${output.stdout}</pre>`;
        }
        
        return `<pre class="output-json">${JSON.stringify(output, null, 2)}</pre>`;
    }

    /**
     * Render hierarchical action menu for widget
     */
    renderActionMenu(widget) {
        if (!widget.actions || Object.keys(widget.actions).length === 0) {
            return '<div class="menu-item-empty">No actions available</div>';
        }

        // Group actions by category
        const categories = {};
        for (const [actionSlug, actionConfig] of Object.entries(widget.actions)) {
            const category = actionConfig.menu_category || 'actions';
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push({
                slug: actionSlug,
                name: actionConfig.names?.en || actionSlug,
                icon: actionConfig.icon || '⚙️',
                description: actionConfig.description?.en || ''
            });
        }

        // Render hierarchical menu
        let menuHtml = '';
        for (const [category, actions] of Object.entries(categories)) {
            menuHtml += `<div class="menu-category">
                <div class="menu-category-header">${category.charAt(0).toUpperCase() + category.slice(1)}</div>`;
            
            for (const action of actions) {
                menuHtml += `
                    <div class="menu-item" onclick="executeWidgetAction('${widget.id}', '${action.slug}')" title="${action.description}">
                        <span class="menu-icon">${action.icon}</span>
                        <span class="menu-text">${action.name}</span>
                    </div>`;
            }
            menuHtml += '</div>';
        }

        return menuHtml;
    }

    /**
     * Render widget connections
     */
    renderWidgetConnections(widget) {
        const inputs = Array.from(widget.connections.inputs.entries());
        const outputs = Array.from(widget.connections.outputs.entries());
        
        if (inputs.length === 0 && outputs.length === 0) {
            return '';
        }
        
        const inputsHtml = inputs.map(([key, sourceWidget]) => 
            `<div class="connection-input">← ${key} from ${sourceWidget}</div>`
        ).join('');
        
        const outputsHtml = outputs.map(([key, targetWidgets]) =>
            `<div class="connection-output">${key} → ${targetWidgets.join(', ')}</div>`
        ).join('');
        
        return `<div class="connections">${inputsHtml}${outputsHtml}</div>`;
    }

    /**
     * Execute widget with Python backend
     */
    async executeWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget || !widget.schema) {
            console.error(`Widget ${widgetId} not found or no schema`);
            return;
        }

        // Update widget status
        widget.status = 'running';
        this.updateWidgetDisplay(widget);
        
        try {
            // Simulate widget execution (in real implementation, this would call Python backend)
            const result = await this.simulateWidgetExecution(widget);
            
            widget.lastOutput = result;
            widget.status = result.success ? 'completed' : 'error';
            
            // Update display
            this.updateWidgetDisplay(widget);
            
            // Trigger dependent widgets
            this.triggerDependentWidgets(widgetId);
            
            console.log(`Widget ${widgetId} executed:`, result);
            return result;
            
        } catch (error) {
            console.error(`Widget execution failed: ${error}`);
            widget.status = 'error';
            widget.lastOutput = { success: false, error: error.message };
            this.updateWidgetDisplay(widget);
        }
    }

    /**
     * Execute specific widget action with validation
     */
    async executeWidgetAction(widgetId, actionSlug) {
        const widget = this.widgets.get(widgetId);
        if (!widget || !widget.schema) {
            console.error(`Widget ${widgetId} not found or no schema`);
            return;
        }

        const action = widget.actions[actionSlug];
        if (!action) {
            console.error(`Action ${actionSlug} not found for widget ${widgetId}`);
            this.updateStatus(`Action '${actionSlug}' not found`, 'error');
            return;
        }

        // Update widget status
        widget.status = 'running';
        this.updateWidgetDisplay(widget);
        
        try {
            // Validate input if required
            if (action.validation_required !== false) {
                const validation = this.validateWidgetInput(widget.config, widget.schema);
                if (!validation.valid) {
                    throw new Error(`Input validation failed: ${validation.errors.join(', ')}`);
                }
            }
            
            // Simulate action-specific execution
            const result = await this.simulateWidgetActionExecution(widget, actionSlug, action);
            
            widget.lastOutput = result;
            widget.status = result.success ? 'completed' : 'error';
            
            // Update display
            this.updateWidgetDisplay(widget);
            
            // Update status with action info
            const actionName = action.names?.en || actionSlug;
            this.updateStatus(`Executed action: ${actionName}`, result.success ? 'success' : 'error');
            
            console.log(`Widget ${widgetId} action ${actionSlug} executed:`, result);
            return result;
            
        } catch (error) {
            console.error(`Widget action execution failed: ${error}`);
            widget.status = 'error';
            widget.lastOutput = { success: false, error: error.message, action_slug: actionSlug };
            this.updateWidgetDisplay(widget);
            this.updateStatus(`Action failed: ${error.message}`, 'error');
        }
    }

    /**
     * Validate widget input against schema
     */
    validateWidgetInput(config, schema) {
        const errors = [];
        const inputSchema = schema.input_schema || schema.input_schemas?.[0];
        
        if (!inputSchema || !inputSchema.properties) {
            return { valid: true, errors: [] };
        }
        
        // Check required fields
        const required = inputSchema.required || [];
        for (const field of required) {
            if (!(field in config) || config[field] === null || config[field] === undefined) {
                errors.push(`Required field '${field}' is missing`);
            }
        }
        
        // Basic type checking
        for (const [field, fieldSchema] of Object.entries(inputSchema.properties)) {
            if (field in config) {
                const value = config[field];
                const expectedType = fieldSchema.type;
                
                if (expectedType === 'integer' && (!Number.isInteger(value) && typeof value !== 'number')) {
                    errors.push(`Field '${field}' must be an integer`);
                } else if (expectedType === 'number' && typeof value !== 'number') {
                    errors.push(`Field '${field}' must be a number`);
                } else if (expectedType === 'string' && typeof value !== 'string') {
                    errors.push(`Field '${field}' must be a string`);
                } else if (expectedType === 'boolean' && typeof value !== 'boolean') {
                    errors.push(`Field '${field}' must be a boolean`);
                }
                
                // Range validation
                if (expectedType === 'integer' || expectedType === 'number') {
                    if ('minimum' in fieldSchema && value < fieldSchema.minimum) {
                        errors.push(`Field '${field}' must be >= ${fieldSchema.minimum}`);
                    }
                    if ('maximum' in fieldSchema && value > fieldSchema.maximum) {
                        errors.push(`Field '${field}' must be <= ${fieldSchema.maximum}`);
                    }
                }
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Simulate action-specific widget execution
     */
    async simulateWidgetActionExecution(widget, actionSlug, actionConfig) {
        await new Promise(resolve => setTimeout(resolve, 300)); // Simulate processing time
        
        const outputFormat = actionConfig.output_format || 'json';
        const actionName = actionConfig.names?.en || actionSlug;
        
        // Generate different outputs based on format
        const result = {
            success: true,
            action_slug: actionSlug,
            action_name: actionName,
            output_format: outputFormat,
            execution_time: Math.random() * 500 + 100
        };
        
        switch (outputFormat) {
            case 'html':
                result.rendered_html = `<div class="action-result">
                    <h3>${actionName} Result</h3>
                    <p>Action executed successfully on ${widget.type} widget.</p>
                    <p><strong>Format:</strong> ${outputFormat}</p>
                    <p><strong>Execution Time:</strong> ${result.execution_time.toFixed(2)}ms</p>
                </div>`;
                break;
            case 'svg':
                result.svg_content = `<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
                    <rect width="200" height="100" fill="#f4e4c1" stroke="#e6d7b8"/>
                    <text x="100" y="30" text-anchor="middle" fill="#6b5544">SVG Output</text>
                    <text x="100" y="50" text-anchor="middle" fill="#6b5544">${actionName}</text>
                    <text x="100" y="70" text-anchor="middle" fill="#6b5544">${widget.type}</text>
                </svg>`;
                break;
            case 'png':
                result.image_data = {
                    base64: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x8ABQABAgDm4+JrAAAAABJRU5ErkJggg==',
                    width: 200,
                    height: 100,
                    format: 'png'
                };
                break;
            case 'pdf':
                result.pdf_data = {
                    size: '2.3KB',
                    pages: 1,
                    download_url: '#pdf-download'
                };
                break;
            case 'markdown':
                result.markdown_content = `# ${actionName} Output\n\n**Widget Type:** ${widget.type}\n\n**Action:** ${actionSlug}\n\n**Result:** Action executed successfully.\n\n---\n\n*Generated at ${new Date().toISOString()}*`;
                break;
            default:
                result.data = {
                    action: actionSlug,
                    widget_type: widget.type,
                    timestamp: new Date().toISOString(),
                    config: widget.config
                };
        }
        
        return result;
    }

    /**
     * Simulate widget execution (replace with actual Python execution)
     */
    async simulateWidgetExecution(widget) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate processing time
        
        const type = widget.type;
        const config = widget.config;
        
        if (type === 'markdown-note') {
            return this.executeMarkdownWidget(config);
        } else if (type === 'python-code') {
            return this.executePythonWidget(config);
        } else if (type === 'data-generator') {
            return this.executeDataGenerator(config);
        } else if (type === 'data-plot') {
            return this.executeDataPlot(config);
        } else {
            return {
                success: true,
                result: `Executed ${type} widget`,
                execution_time: 123
            };
        }
    }

    /**
     * Execute markdown widget with variable substitution
     */
    executeMarkdownWidget(config) {
        let content = config.content || '';
        const variables = config.variables || {};
        
        // Find and substitute variables
        const variablePattern = /\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}/g;
        const variablesUsed = [];
        
        content = content.replace(variablePattern, (match, varName) => {
            variablesUsed.push(varName);
            if (varName in variables) {
                return String(variables[varName]);
            } else {
                return `{undefined:${varName}}`;
            }
        });
        
        // Simple markdown to HTML
        let html = content
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        return {
            success: true,
            rendered_html: html,
            variables_used: variablesUsed,
            substituted_content: content
        };
    }

    /**
     * Execute Python widget
     */
    executePythonWidget(config) {
        const code = config.code || '';
        
        // This would normally execute Python code via Pyodide
        // For now, simulate execution
        return {
            success: true,
            result: null,
            stdout: '# Code executed successfully\nHello from Python!',
            stderr: '',
            variables: {
                'x': [1, 2, 3, 4, 5],
                'y': [1, 4, 9, 16, 25]
            }
        };
    }

    /**
     * Execute data generator widget
     */
    executeDataGenerator(config) {
        const type = config.type || 'sine';
        const nPoints = config.n_points || 100;
        const xRange = config.x_range || { min: 0, max: 10 };
        const params = config.parameters || {};
        
        // Generate data
        const x = [];
        const y = [];
        
        for (let i = 0; i < nPoints; i++) {
            const xi = xRange.min + (i / (nPoints - 1)) * (xRange.max - xRange.min);
            x.push(xi);
            
            let yi = 0;
            if (type === 'sine') {
                yi = (params.amplitude || 1) * Math.sin((params.frequency || 1) * xi + (params.phase || 0));
            } else if (type === 'linear') {
                yi = (params.slope || 1) * xi + (params.phase || 0);
            } else if (type === 'random') {
                yi = (params.amplitude || 1) * Math.random();
            }
            
            // Add noise
            if (params.noise) {
                yi += params.noise * (Math.random() - 0.5) * 2;
            }
            
            y.push(yi);
        }
        
        return {
            success: true,
            data: { x, y },
            metadata: {
                generator_type: type,
                parameters_used: params,
                generated_at: new Date().toISOString()
            }
        };
    }

    /**
     * Trigger execution of widgets that depend on the given widget
     */
    async triggerDependentWidgets(sourceId) {
        const sourceWidget = this.widgets.get(sourceId);
        if (!sourceWidget || !sourceWidget.lastOutput || !sourceWidget.lastOutput.success) {
            return;
        }
        
        // Find widgets that have this widget as input
        for (const [widgetId, widget] of this.widgets) {
            if (widget.connections.inputs.size > 0) {
                for (const [inputPath, connectedSourceId] of widget.connections.inputs) {
                    if (connectedSourceId === sourceId) {
                        // Update the target widget's config with output data
                        this.updateWidgetInputFromConnection(widget, inputPath, sourceWidget.lastOutput);
                        
                        // Execute the dependent widget
                        await this.executeWidget(widgetId);
                        break;
                    }
                }
            }
        }
    }

    /**
     * Update widget input configuration from connected output
     */
    updateWidgetInputFromConnection(targetWidget, inputPath, sourceOutput) {
        // Simple path resolution - in practice this would be more sophisticated
        const pathParts = inputPath.split('.');
        let current = targetWidget.config;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
            if (!(pathParts[i] in current)) {
                current[pathParts[i]] = {};
            }
            current = current[pathParts[i]];
        }
        
        // Set the value from source output
        const finalKey = pathParts[pathParts.length - 1];
        if (sourceOutput.data) {
            current[finalKey] = sourceOutput.data;
        } else if (sourceOutput.result) {
            current[finalKey] = sourceOutput.result;
        }
    }

    /**
     * Update widget display
     */
    updateWidgetDisplay(widget) {
        const element = document.querySelector(`[data-widget-id="${widget.id}"]`);
        if (!element) return;
        
        // Update status class
        element.className = `board-widget widget-${widget.type} status-${widget.status}`;
        
        // Update status icon
        const statusElement = element.querySelector('.widget-status');
        if (statusElement) {
            statusElement.innerHTML = this.getStatusIcon(widget.status);
            statusElement.className = `widget-status ${widget.status === 'running' ? 'fa-spin' : ''}`;
        }
        
        // Update content
        const contentElement = element.querySelector('.widget-content');
        if (contentElement) {
            contentElement.innerHTML = this.renderWidgetContent(widget);
        }
    }

    /**
     * Make widget draggable
     */
    makeDraggable(element) {
        let isDragging = false;
        let startX, startY, initialX, initialY;

        const header = element.querySelector('.widget-header');
        
        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = element.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;
            
            element.classList.add('dragging');
            this.selectWidget(element.dataset.widgetId);
            
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            element.style.left = (initialX + dx) + 'px';
            element.style.top = (initialY + dy) + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.classList.remove('dragging');
                
                // Update widget position
                const widget = this.widgets.get(element.dataset.widgetId);
                if (widget) {
                    widget.x = parseInt(element.style.left);
                    widget.y = parseInt(element.style.top);
                    this.saveBoardToStorage();
                }
            }
        });
    }

    /**
     * Select widget
     */
    selectWidget(widgetId) {
        // Deselect all widgets
        this.deselectAllWidgets();
        
        // Select this widget
        const element = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (element) {
            element.classList.add('selected');
            this.selectedWidget = widgetId;
        }
    }

    /**
     * Deselect all widgets
     */
    deselectAllWidgets() {
        document.querySelectorAll('.board-widget.selected').forEach(el => {
            el.classList.remove('selected');
        });
        this.selectedWidget = null;
    }

    /**
     * Delete widget
     */
    deleteWidget(widgetId) {
        const element = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (element) {
            element.remove();
        }
        
        this.widgets.delete(widgetId);
        this.saveBoardToStorage();
        this.updateStatus('Widget deleted', 'success');
    }

    /**
     * Save board to localStorage
     */
    saveBoardToStorage() {
        const boardData = {
            title: 'Mathematical Workspace',
            widgets: Array.from(this.widgets.entries()).map(([id, widget]) => ({
                id: widget.id,
                type: widget.type,
                x: widget.x,
                y: widget.y,
                width: widget.width,
                height: widget.height,
                config: widget.config,
                connections: {
                    inputs: Array.from(widget.connections.inputs.entries()),
                    outputs: Array.from(widget.connections.outputs.entries())
                }
            })),
            meta: {
                savedAt: new Date().toISOString(),
                version: '1.0'
            }
        };
        
        localStorage.setItem('weierstrass_board', JSON.stringify(boardData));
        console.log('Board saved:', boardData);
    }

    /**
     * Load board from localStorage
     */
    loadBoardFromStorage() {
        const savedData = localStorage.getItem('weierstrass_board');
        if (!savedData) return;
        
        try {
            const boardData = JSON.parse(savedData);
            
            // Clear current board
            this.widgets.clear();
            document.getElementById('board-content').innerHTML = '';
            
            // Restore widgets
            boardData.widgets.forEach(widgetData => {
                if (this.widgetSchemas && this.widgetSchemas['widget-schemas'][widgetData.type]) {
                    const widget = this.createWidget(widgetData.type, widgetData.x, widgetData.y, widgetData.config);
                    if (widget) {
                        widget.width = widgetData.width;
                        widget.height = widgetData.height;
                        
                        // Restore connections
                        if (widgetData.connections) {
                            widget.connections.inputs = new Map(widgetData.connections.inputs);
                            widget.connections.outputs = new Map(widgetData.connections.outputs);
                        }
                    }
                }
            });
            
            console.log('Board loaded:', boardData);
            
        } catch (error) {
            console.error('Failed to load board:', error);
        }
    }

    /**
     * Update status message
     */
    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-${type}`;
            
            // Auto-clear after delay
            setTimeout(() => {
                statusElement.textContent = 'Board Ready';
                statusElement.className = '';
            }, 3000);
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Auto-adjust layout mode based on screen size
        const isMobile = window.innerWidth < 1024;
        const defaultMode = isMobile ? 'mobile' : 'desktop';
        setLayoutMode(defaultMode);
    }

    /**
     * Initialize user preferences
     */
    initializeUserPreferences() {
        // Set theme
        const savedTheme = localStorage.getItem('weierstrass_theme') || 'dark';
        setTheme(savedTheme);
        
        // Set layout mode
        const isMobile = window.innerWidth < 1024;
        const defaultMode = isMobile ? 'mobile' : 'desktop';
        setLayoutMode(defaultMode);
    }
}

// ===== WIDGET GRAPH CLASS =====
class WidgetGraph {
    constructor() {
        this.widgets = new Map();
        this.connections = new Map();
    }
    
    addWidget(id, widget) {
        this.widgets.set(id, widget);
    }
    
    removeWidget(id) {
        this.widgets.delete(id);
        this.connections.delete(id);
    }
    
    connectWidgets(sourceId, targetId, outputPath, inputPath) {
        if (!this.connections.has(sourceId)) {
            this.connections.set(sourceId, []);
        }
        
        this.connections.get(sourceId).push({
            target: targetId,
            outputPath,
            inputPath
        });
    }
}

// ===== GLOBAL FUNCTIONS =====

let boardApp;

/**
 * Widget management functions
 */
function editWidget(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget || !widget.schema) return;
    
    const editor = document.getElementById('widget-editor');
    const title = document.getElementById('editor-title');
    const body = document.getElementById('editor-body');
    
    title.textContent = `Configure ${widget.title}`;
    
    // Generate form based on JSON schema
    const editorHTML = generateSchemaForm(widget.schema.input_schema, widget.config);
    
    body.innerHTML = editorHTML;
    editor.style.display = 'flex';
    
    // Store current widget for saving
    editor.dataset.widgetId = widgetId;
}

function generateSchemaForm(inputSchema, currentConfig) {
    if (!inputSchema || !inputSchema.properties) {
        return '<p>No configuration options available</p>';
    }
    
    let formHTML = '<div class="schema-form">';
    
    Object.entries(inputSchema.properties).forEach(([key, propSchema]) => {
        const currentValue = currentConfig[key] ?? propSchema.default ?? '';
        const description = propSchema.description || '';
        const required = inputSchema.required?.includes(key) ? ' *' : '';
        
        formHTML += `
            <div class="form-group">
                <label for="config-${key}">${key}${required}</label>
                <p class="form-description">${description}</p>
                ${generateFormField(key, propSchema, currentValue)}
            </div>
        `;
    });
    
    formHTML += '</div>';
    
    // Add variable editor for markdown widgets
    if (inputSchema.properties.variables) {
        formHTML += generateVariableEditor(currentConfig.variables || {});
    }
    
    return formHTML;
}

function generateFormField(key, propSchema, currentValue) {
    const fieldId = `config-${key}`;
    const type = propSchema.type;
    const style = 'width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary);';
    
    if (type === 'string' && propSchema.enum) {
        // Dropdown
        const options = propSchema.enum.map(option => 
            `<option value="${option}" ${option === currentValue ? 'selected' : ''}>${option}</option>`
        ).join('');
        return `<select id="${fieldId}" style="${style}">${options}</select>`;
        
    } else if (type === 'boolean') {
        // Checkbox
        return `<input type="checkbox" id="${fieldId}" ${currentValue ? 'checked' : ''}> Yes`;
        
    } else if (type === 'number' || type === 'integer') {
        // Number input
        const min = propSchema.minimum !== undefined ? `min="${propSchema.minimum}"` : '';
        const max = propSchema.maximum !== undefined ? `max="${propSchema.maximum}"` : '';
        const step = type === 'integer' ? 'step="1"' : 'step="any"';
        return `<input type="number" id="${fieldId}" value="${currentValue}" ${min} ${max} ${step} style="${style}">`;
        
    } else if (type === 'string' && (currentValue.includes('\n') || propSchema.description?.includes('content'))) {
        // Textarea for multi-line strings
        return `<textarea id="${fieldId}" rows="8" style="${style}">${currentValue}</textarea>`;
        
    } else {
        // Text input
        return `<input type="text" id="${fieldId}" value="${currentValue}" style="${style}">`;
    }
}

function generateVariableEditor(variables) {
    let variablesHTML = '<div class="variables-editor"><h4>Variables</h4>';
    
    Object.entries(variables).forEach(([name, value]) => {
        variablesHTML += `
            <div class="variable-row">
                <input type="text" placeholder="Variable name" value="${name}" class="var-name" style="width: 40%; margin-right: 10px;">
                <input type="text" placeholder="Value" value="${value}" class="var-value" style="width: 40%; margin-right: 10px;">
                <button type="button" onclick="removeVariable(this)" style="width: 15%;">Remove</button>
            </div>
        `;
    });
    
    variablesHTML += `
        <button type="button" onclick="addVariable()" style="margin-top: 10px;">Add Variable</button>
        </div>
    `;
    
    return variablesHTML;
}

function addVariable() {
    const container = document.querySelector('.variables-editor');
    const newRow = document.createElement('div');
    newRow.className = 'variable-row';
    newRow.innerHTML = `
        <input type="text" placeholder="Variable name" class="var-name" style="width: 40%; margin-right: 10px;">
        <input type="text" placeholder="Value" class="var-value" style="width: 40%; margin-right: 10px;">
        <button type="button" onclick="removeVariable(this)" style="width: 15%;">Remove</button>
    `;
    container.insertBefore(newRow, container.lastElementChild);
}

function removeVariable(button) {
    button.parentElement.remove();
}

function saveWidget() {
    const editor = document.getElementById('widget-editor');
    const widgetId = editor.dataset.widgetId;
    const widget = boardApp.widgets.get(widgetId);
    
    if (!widget) return;
    
    // Collect form data
    const newConfig = {};
    const schema = widget.schema.input_schema;
    
    if (schema && schema.properties) {
        Object.keys(schema.properties).forEach(key => {
            const field = document.getElementById(`config-${key}`);
            if (field) {
                if (field.type === 'checkbox') {
                    newConfig[key] = field.checked;
                } else if (field.type === 'number') {
                    newConfig[key] = parseFloat(field.value) || 0;
                } else {
                    newConfig[key] = field.value;
                }
            }
        });
    }
    
    // Collect variables if present
    const variableRows = document.querySelectorAll('.variable-row');
    if (variableRows.length > 0) {
        const variables = {};
        variableRows.forEach(row => {
            const name = row.querySelector('.var-name').value.trim();
            const value = row.querySelector('.var-value').value;
            if (name) {
                variables[name] = value;
            }
        });
        newConfig.variables = variables;
    }
    
    // Update widget configuration
    widget.config = newConfig;
    widget.status = 'idle'; // Reset status
    
    // Update display
    boardApp.updateWidgetDisplay(widget);
    
    // Save board
    boardApp.saveBoardToStorage();
    boardApp.updateStatus('Widget configuration saved', 'success');
    
    closeEditor();
}

function runWidget(widgetId) {
    boardApp.executeWidget(widgetId);
}

function executeWidgetAction(widgetId, actionSlug) {
    boardApp.executeWidgetAction(widgetId, actionSlug);
    // Close the hamburger menu
    const menu = document.getElementById(`menu-${widgetId}`);
    if (menu) {
        menu.style.display = 'none';
    }
}

function toggleWidgetMenu(widgetId) {
    const menu = document.getElementById(`menu-${widgetId}`);
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
    
    // Close other open menus
    document.querySelectorAll('.hamburger-dropdown').forEach(dropdown => {
        if (dropdown.id !== `menu-${widgetId}`) {
            dropdown.style.display = 'none';
        }
    });
}

function connectWidget(widgetId) {
    // Simple connection interface - in practice this would be more sophisticated
    const sourceId = prompt('Connect FROM widget ID:');
    const outputPath = prompt('Output path (e.g., data.x):') || 'result';
    const inputPath = prompt('Input path (e.g., data):') || 'data';
    
    if (sourceId && sourceId !== widgetId) {
        boardApp.connectWidgets(sourceId, widgetId, outputPath, inputPath);
        boardApp.updateStatus(`Connected ${sourceId} → ${widgetId}`, 'success');
    }
}

function closeEditor() {
    document.getElementById('widget-editor').style.display = 'none';
}

function deleteWidget(widgetId) {
    if (confirm('Delete this widget?')) {
        boardApp.deleteWidget(widgetId);
    }
}

/**
 * Control panel functions
 */
function toggleControlPanel() {
    const panel = document.getElementById('global-controls');
    const icon = document.getElementById('panel-toggle-icon');
    
    panel.classList.toggle('expanded');
    
    if (panel.classList.contains('expanded')) {
        icon.className = 'fas fa-chevron-down';
    } else {
        icon.className = 'fas fa-chevron-up';
    }
}

function toggleLibrary() {
    const library = document.querySelector('.widget-library');
    if (window.innerWidth <= 768) {
        library.classList.toggle('open');
    } else {
        // Desktop: hide/show library
        const body = document.body;
        body.style.gridTemplateColumns = library.style.display === 'none' 
            ? 'var(--library-width) 1fr' 
            : '0 1fr';
        library.style.display = library.style.display === 'none' ? 'flex' : 'none';
    }
}

function fitToScreen() {
    // TODO: Implement fit to screen functionality
    boardApp.updateStatus('Fit to screen', 'success');
}

function toggleGrid() {
    const boardContent = document.getElementById('board-content');
    boardContent.classList.toggle('no-grid');
    boardApp.gridEnabled = !boardApp.gridEnabled;
    boardApp.updateStatus(`Grid ${boardApp.gridEnabled ? 'enabled' : 'disabled'}`, 'success');
}

function saveBoard() {
    boardApp.saveBoardToStorage();
    boardApp.updateStatus('Board saved', 'success');
}

function loadBoard() {
    boardApp.loadBoardFromStorage();
    boardApp.updateStatus('Board loaded', 'success');
}

function exportBoard() {
    const boardData = {
        title: 'Mathematical Workspace',
        widgets: Array.from(boardApp.widgets.entries()).map(([id, widget]) => ({
            id: widget.id,
            type: widget.type,
            x: widget.x,
            y: widget.y,
            width: widget.width,
            height: widget.height,
            config: widget.config
        }))
    };
    
    const blob = new Blob([JSON.stringify(boardData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mathematical-board.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    boardApp.updateStatus('Board exported', 'success');
}

function playAllWidgets() {
    boardApp.updateStatus('Running all widgets...', 'computing');
    
    const widgetIds = Array.from(boardApp.widgets.keys());
    let completed = 0;
    
    widgetIds.forEach(widgetId => {
        boardApp.executeWidget(widgetId).then(() => {
            completed++;
            if (completed === widgetIds.length) {
                boardApp.updateStatus('All widgets executed', 'success');
            }
        });
    });
}

function pauseAllWidgets() {
    boardApp.updateStatus('Paused all widgets', 'paused');
    // TODO: Pause all running widgets
}

function clearBoard() {
    if (confirm('Clear all widgets from the board?')) {
        boardApp.widgets.clear();
        document.getElementById('board-content').innerHTML = '';
        boardApp.saveBoardToStorage();
        boardApp.updateStatus('Board cleared', 'success');
    }
}

/**
 * Layout and theme functions
 */
function setLayoutMode(mode) {
    const body = document.body;
    
    body.classList.remove('desktop-mode', 'mobile-mode');
    body.classList.add(`${mode}-mode`);
    
    // Update button states
    document.querySelectorAll('.control-section .control-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeButton = document.getElementById(`${mode}-mode-btn`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    console.log(`Layout mode set to: ${mode}`);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.innerHTML = theme === 'dark' ? '🌙' : '☀️';
    }
    
    localStorage.setItem('weierstrass_theme', theme);
    console.log(`Theme set to: ${theme}`);
}

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    boardApp = new MathematicalBoard();
    window.boardApp = boardApp; // Make globally available
    
    console.log('Mathematical Board initialized');
});