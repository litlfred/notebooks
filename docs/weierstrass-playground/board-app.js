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
        this.pyodide = null; // Python execution engine
        this.pyodideLoading = false;
        this.runningWidgets = new Set(); // Track running widgets for stop functionality
        this.eventListeners = new Map(); // Event system for widget communication
        this.slugCounters = new Map(); // Track instance counts by widget slug
        
        this.initializeBoard();
        this.setupEventListeners();
        this.initializeUserPreferences();
        this.loadWidgetSchemas();
        this.initializePython();
    }

    /**
     * Initialize Python execution environment
     */
    async initializePython() {
        if (this.pyodideLoading || this.pyodide) return;
        
        this.pyodideLoading = true;
        this.updateStatus('Loading Python environment...', 'info');
        
        try {
            // Load Pyodide from CDN
            const pyodideScript = document.createElement('script');
            pyodideScript.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';
            pyodideScript.onload = async () => {
                try {
                    this.pyodide = await loadPyodide({
                        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
                    });
                    
                    // Install commonly used packages
                    await this.pyodide.loadPackage(['numpy', 'matplotlib', 'scipy']);
                    
                    // Set up Python environment with our modules
                    await this.setupPythonEnvironment();
                    
                    this.updateStatus('Python environment ready', 'success');
                    console.log('Pyodide initialized successfully');
                } catch (error) {
                    console.error('Pyodide initialization failed:', error);
                    this.updateStatus('Python environment failed to load', 'error');
                }
                this.pyodideLoading = false;
            };
            pyodideScript.onerror = () => {
                console.error('Failed to load Pyodide script');
                this.updateStatus('Failed to load Python environment', 'error');
                this.pyodideLoading = false;
            };
            
            document.head.appendChild(pyodideScript);
            
        } catch (error) {
            console.error('Python initialization error:', error);
            this.updateStatus('Python environment error', 'error');
            this.pyodideLoading = false;
        }
    }

    /**
     * Setup Python environment with widget framework modules
     */
    async setupPythonEnvironment() {
        if (!this.pyodide) return;

        // Create widget execution framework in Python
        const frameworkCode = `
import sys
import json
import traceback
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import base64

class WidgetExecutor:
    """Base class for widget execution with input validation and error handling"""
    
    def __init__(self, widget_id, widget_type, config, connections=None):
        self.widget_id = widget_id
        self.widget_type = widget_type  
        self.config = config or {}
        self.connections = connections or {}
        self.stdout_buffer = StringIO()
        self.stderr_buffer = StringIO()
        self.variables = {}
        self.result = None
        self.status = 'idle'
        
    def execute(self):
        """Execute widget with error handling and output capture"""
        self.status = 'running'
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Redirect output
            sys.stdout = self.stdout_buffer
            sys.stderr = self.stderr_buffer
            
            # Clear previous output
            self.stdout_buffer.seek(0)
            self.stdout_buffer.truncate(0)
            self.stderr_buffer.seek(0) 
            self.stderr_buffer.truncate(0)
            
            # Execute widget-specific code
            self.result = self._execute_impl()
            self.status = 'completed'
            
            return {
                'success': True,
                'result': self.result,
                'stdout': self.stdout_buffer.getvalue(),
                'stderr': self.stderr_buffer.getvalue(),
                'variables': self.variables,
                'status': self.status
            }
            
        except Exception as e:
            self.status = 'error'
            error_traceback = traceback.format_exc()
            sys.stderr.write(error_traceback)
            
            return {
                'success': False,
                'error': str(e),
                'traceback': error_traceback,
                'stdout': self.stdout_buffer.getvalue(),
                'stderr': self.stderr_buffer.getvalue(), 
                'variables': self.variables,
                'status': self.status
            }
            
        finally:
            # Restore output
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    def _execute_impl(self):
        """Override this method in widget implementations"""
        raise NotImplementedError("Subclasses must implement _execute_impl")
    
    def stop(self):
        """Stop widget execution"""
        self.status = 'stopped'
        # In a real implementation, this would interrupt execution
        print(f"Widget {self.widget_id} execution stopped")

class PythonCodeWidget(WidgetExecutor):
    """Execute arbitrary Python code"""
    
    def _execute_impl(self):
        code = self.config.get('code', '')
        if not code.strip():
            return "No code to execute"
            
        # Execute the code in current namespace
        exec(code, globals(), self.variables)
        
        # Return any variables that were created
        return {
            'code_executed': True,
            'variables_created': list(self.variables.keys())
        }

class WeierstraussWidget(WidgetExecutor):
    """Weierstrass function visualization widget"""
    
    def _execute_impl(self):
        p = self.config.get('p', 5)
        q = self.config.get('q', 7) 
        N = self.config.get('N', 2)
        
        # Generate Weierstrass field visualization
        return self._generate_weierstrass_plot(p, q, N)
    
    def _generate_weierstrass_plot(self, p, q, N):
        # Simple Weierstrass function implementation
        import numpy as np
        import matplotlib.pyplot as plt
        
        x = np.linspace(0, p, 50)
        y = np.linspace(0, q, 50)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        # Simplified Weierstrass function
        W = np.zeros_like(Z, dtype=complex)
        for m in range(-N, N+1):
            for n in range(-N, N+1):
                if m == 0 and n == 0:
                    continue
                omega = m * p + n * 1j * q
                W += 1.0 / (Z - omega)**2
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 6))
        magnitude = np.abs(W)
        magnitude = np.where(magnitude < 100, magnitude, np.nan)  # Mask poles
        
        im = ax.imshow(magnitude, extent=[0, p, 0, q], cmap='viridis', origin='lower')
        ax.set_title(f'Weierstrass ℘ Function (p={p}, q={q})')
        ax.set_xlabel('Re(z)')
        ax.set_ylabel('Im(z)')
        plt.colorbar(im, ax=ax, label='|℘(z)|')
        
        # Save plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        self.variables.update({
            'p': p, 'q': q, 'N': N,
            'field_data': W,
            'plot_image': f'data:image/png;base64,{image_base64}'
        })
        
        return {
            'plot_generated': True,
            'image_data': f'data:image/png;base64,{image_base64}',
            'parameters': {'p': p, 'q': q, 'N': N}
        }

# Global widget registry
_widget_executors = {
    'python-code': PythonCodeWidget,
    'weierstrass': WeierstraussWidget,
    'wp-two-panel': WeierstraussWidget,
    'wp-three-panel': WeierstraussWidget, 
    'wp-five-panel': WeierstraussWidget
}

def execute_widget(widget_id, widget_type, config, connections=None):
    """Execute a widget and return results"""
    executor_class = _widget_executors.get(widget_type, PythonCodeWidget)
    executor = executor_class(widget_id, widget_type, config, connections)
    return executor.execute()

def stop_widget(widget_id):
    """Stop a running widget"""
    # In a full implementation, we'd track running executors
    print(f"Stopping widget {widget_id}")
    return {'stopped': True}
`;

        await this.pyodide.runPython(frameworkCode);
        console.log('Python widget framework initialized');
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
     * Create a new widget using enhanced ID management and event system
     */
    createWidget(type, x, y, customConfig = {}) {
        if (!this.widgetSchemas || !this.widgetSchemas['widget-schemas'][type]) {
            console.error(`Widget schema not found for type: ${type}`);
            return;
        }

        const schema = this.widgetSchemas['widget-schemas'][type];
        
        // Use enhanced widget creation with proper ID management
        const widget = this.createWidgetWithId(type, { x, y }, schema);
        
        // Override config if provided
        if (Object.keys(customConfig).length > 0) {
            widget.config = { ...widget.config, ...customConfig };
        }
        
        // Set widget dimensions and additional properties
        widget.x = x;
        widget.y = y;
        widget.width = 350;
        widget.height = 250;
        widget.title = schema.name;
        widget.icon = schema.icon;
        widget.description = schema.description;

        // Create DOM element
        const element = this.createWidgetElement(widget);
        
        // Add to board
        document.getElementById('board-content').appendChild(element);
        
        // Make draggable
        this.makeDraggable(element);
        
        // Auto-select new widget
        this.selectWidget(widget.id);
        
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
                    <button class="widget-btn stop-btn" onclick="stopWidget('${widget.id}')" title="Stop Execution" ${widget.status !== 'running' ? 'style="display:none"' : ''}>
                        ⏹️
                    </button>
                    <button class="widget-btn" onclick="connectWidget('${widget.id}')" title="Connect">
                        🔗
                    </button>
                    <button class="widget-btn" onclick="toggleAttachedNote('${widget.id}')" title="Toggle Note">
                        📝
                    </button>
                    <button class="widget-btn" onclick="deleteWidget('${widget.id}')" title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
            <div class="widget-content" id="content-${widget.id}">
                ${this.renderWidgetContent(widget)}
            </div>
            <div class="widget-attached-note" id="note-${widget.id}" ${!widget.attachedNote.visible ? 'style="display:none"' : ''}>
                ${this.renderAttachedNote(widget)}
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

        // Special handling for sticky note widget
        if (widget.schema.id === 'sticky-note') {
            return this.renderStickyNoteContent(widget);
        }

        // Show configuration preview for other widgets
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
     * Render sticky note content with markdown display/edit modes and TinyMCE integration
     */
    renderStickyNoteContent(widget) {
        const markdownContent = widget.config.content || '# New Note\n\nEdit to add content...';
        const isEditMode = widget.editMode || false;
        const theme = widget.config.theme || 'desert';
        
        if (isEditMode) {
            // Use Monaco Editor for better markdown editing with LaTeX support
            return `
                <div class="sticky-note-editor">
                    <div class="editor-toolbar">
                        <button class="editor-btn save-btn" onclick="boardApp.saveStickyNote('${widget.id}')">💾 Save</button>
                        <button class="editor-btn cancel-btn" onclick="boardApp.cancelStickyNoteEdit('${widget.id}')">❌ Cancel</button>
                        <select class="theme-selector" onchange="boardApp.changeStickyTheme('${widget.id}', this.value)">
                            <option value="desert" ${theme === 'desert' ? 'selected' : ''}>🏜️ Desert</option>
                            <option value="classic" ${theme === 'classic' ? 'selected' : ''}>💛 Classic</option>
                            <option value="ocean" ${theme === 'ocean' ? 'selected' : ''}>🌊 Ocean</option>
                            <option value="forest" ${theme === 'forest' ? 'selected' : ''}>🌲 Forest</option>
                            <option value="lavender" ${theme === 'lavender' ? 'selected' : ''}>💜 Lavender</option>
                            <option value="mint" ${theme === 'mint' ? 'selected' : ''}>🌿 Mint</option>
                        </select>
                        <div class="editor-help">
                            <button class="editor-btn help-btn" onclick="boardApp.toggleMarkdownHelp('${widget.id}')" title="Markdown Help">❓</button>
                        </div>
                    </div>
                    <div id="markdown-help-${widget.id}" class="markdown-help" style="display: none;">
                        <div class="help-content">
                            <h4>Markdown & LaTeX Support</h4>
                            <p><strong>Headers:</strong> # H1, ## H2, ### H3</p>
                            <p><strong>Emphasis:</strong> *italic*, **bold**, ~~strikethrough~~</p>
                            <p><strong>Lists:</strong> - item or 1. item</p>
                            <p><strong>Links:</strong> [text](url)</p>
                            <p><strong>Code:</strong> \`inline\` or \`\`\`block\`\`\`</p>
                            <p><strong>Math:</strong> $inline$ or $$block$$</p>
                            <p><strong>Variables:</strong> {{variable_name}} - access widget values</p>
                        </div>
                    </div>
                    <div class="editor-container" id="editor-container-${widget.id}" 
                         style="height: calc(100% - 120px); border: 1px solid var(--current-sticky-border);">
                        <textarea class="sticky-note-textarea" id="editor-${widget.id}" 
                            style="width: 100%; height: 100%; border: none; padding: 1rem; 
                                   background: var(--current-sticky-content); color: var(--current-sticky-text);
                                   font-family: 'Monaco', 'Menlo', 'Courier New', monospace; 
                                   font-size: 0.9rem; resize: none; outline: none;"
                            placeholder="Enter markdown content with LaTeX support...">${this.escapeHtml(markdownContent)}</textarea>
                    </div>
                </div>
            `;
        } else {
            // Display mode - show rendered markdown with variable substitution
            const processedContent = this.processMarkdownVariables(markdownContent, widget);
            return `
                <div class="sticky-note-display" onclick="boardApp.editStickyNote('${widget.id}')" 
                     style="cursor: pointer; height: 100%; position: relative; padding: 1rem;">
                    <div class="markdown-content" style="height: calc(100% - 2rem); overflow-y: auto;">
                        ${this.renderMarkdown(processedContent)}
                    </div>
                    <div class="edit-hint" style="position: absolute; bottom: 5px; right: 5px; 
                         font-size: 0.7rem; opacity: 0.6; background: rgba(0,0,0,0.1); 
                         padding: 2px 6px; border-radius: 3px;">✏️ Click to edit</div>
                </div>
            `;
        }
    }

    /**
     * Simple markdown renderer with LaTeX support
     */
    renderMarkdown(content) {
        // Basic markdown parsing
        let html = content
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/`([^`]+)`/gim, '<code>$1</code>')
            .replace(/\n\n/gim, '</p><p>')
            .replace(/\n/gim, '<br>');
            
        // Wrap in paragraphs if not already wrapped
        if (!html.includes('<h') && !html.includes('<p>')) {
            html = '<p>' + html + '</p>';
        }
            
        // Basic LaTeX symbol support
        html = html
            .replace(/\\wp/g, '℘')
            .replace(/\\Z/g, 'ℤ')
            .replace(/\\C/g, 'ℂ')
            .replace(/\\R/g, 'ℝ')
            .replace(/\\L/g, 'L')
            .replace(/\\T/g, 'T');
            
        return html;
    }

    /**
     * Toggle sticky note edit mode
     */
    editStickyNote(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        widget.editMode = true;
        this.updateWidgetDisplay(widget);
    }

    /**
     * Save sticky note content
     */
    saveStickyNote(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        const textarea = document.getElementById(`editor-${widgetId}`);
        if (textarea) {
            widget.config.content = textarea.value;
            widget.editMode = false;
            this.updateWidgetDisplay(widget);
            this.saveBoardToStorage();
        }
    }

    /**
     * Cancel sticky note edit
     */
    cancelStickyNoteEdit(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        widget.editMode = false;
        this.updateWidgetDisplay(widget);
    }

    /**
     * Change sticky note theme
     */
    changeStickyTheme(widgetId, theme) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        widget.config.theme = theme;
        // Update the widget element class
        widget.element.className = widget.element.className.replace(/theme-\w+/g, '') + ` theme-${theme}`;
        this.saveBoardToStorage();
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
     * Render attached note for widget with dynamic variable substitution
     */
    renderAttachedNote(widget) {
        if (!widget.attachedNote) return '';
        
        const note = widget.attachedNote;
        const isEditMode = note.editMode || false;
        
        if (isEditMode) {
            return `
                <div class="attached-note-editor">
                    <div class="note-toolbar">
                        <button class="editor-btn save-note-btn" onclick="boardApp.saveAttachedNote('${widget.id}')">💾 Save</button>
                        <button class="editor-btn cancel-note-btn" onclick="boardApp.cancelAttachedNoteEdit('${widget.id}')">❌ Cancel</button>
                        <div class="note-help">
                            <small>Use {{config}} for configuration, {{output}} for results, {{widget.id}} for instance ID</small>
                        </div>
                    </div>
                    <textarea class="attached-note-textarea" id="note-editor-${widget.id}" 
                        style="width: 100%; height: 150px; padding: 0.5rem; border: 1px solid var(--border-color); 
                               border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary);
                               font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 0.85rem;"
                        placeholder="Enter markdown notes with dynamic variables...">${this.escapeHtml(note.content)}</textarea>
                </div>
            `;
        } else {
            // Display mode - show rendered markdown with variable substitution
            const processedContent = this.processNoteVariables(note.content, widget);
            return `
                <div class="attached-note-display" onclick="boardApp.editAttachedNote('${widget.id}')" 
                     style="cursor: pointer; padding: 0.5rem; border: 1px solid var(--border-color);
                            border-radius: 4px; background: var(--bg-tertiary); margin-top: 0.5rem;">
                    <div class="note-content" style="font-size: 0.85rem;">
                        ${this.renderMarkdown(processedContent)}
                    </div>
                    <div class="note-edit-hint" style="font-size: 0.7rem; color: var(--text-secondary); 
                         text-align: right; margin-top: 0.25rem;">
                        📝 Click to edit note
                    </div>
                </div>
            `;
        }
    }

    /**
     * Process dynamic variables in attached note content  
     */
    processNoteVariables(content, widget) {
        if (!content) return '';
        
        let processed = content;
        
        // Update attached note variables
        this.updateAttachedNoteVariables(widget);
        
        // Replace dynamic variables
        for (const [key, value] of widget.attachedNote.variables) {
            const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
            processed = processed.replace(regex, value);
        }
        
        // Replace common widget variables
        processed = processed.replace(/\{\{widget\.id\}\}/g, widget.id);
        processed = processed.replace(/\{\{widget\.type\}\}/g, widget.type);
        processed = processed.replace(/\{\{widget\.status\}\}/g, widget.status);
        
        // Replace config object
        try {
            const configJson = JSON.stringify(widget.config, null, 2);
            processed = processed.replace(/\{\{config\}\}/g, `\`\`\`json\n${configJson}\n\`\`\``);
        } catch (e) {
            processed = processed.replace(/\{\{config\}\}/g, '[Config Error]');
        }
        
        // Replace output object
        if (widget.lastOutput) {
            try {
                const outputJson = JSON.stringify(widget.lastOutput, null, 2);
                processed = processed.replace(/\{\{output\}\}/g, `\`\`\`json\n${outputJson}\n\`\`\``);
            } catch (e) {
                processed = processed.replace(/\{\{output\}\}/g, '[Output Error]');
            }
        } else {
            processed = processed.replace(/\{\{output\}\}/g, '*No output yet*');
        }
        
        return processed;
    }

    /**
     * Update dynamic variables in attached note based on widget state
     */
    updateAttachedNoteVariables(widget) {
        if (!widget.attachedNote.variables) {
            widget.attachedNote.variables = new Map();
        }
        
        const vars = widget.attachedNote.variables;
        
        // Update execution info
        vars.set('last_executed', widget.lastOutput ? new Date().toLocaleString() : 'Never');
        vars.set('execution_status', widget.status);
        
        // Update from last output variables if available
        if (widget.lastOutput && widget.lastOutput.variables) {
            for (const [key, value] of Object.entries(widget.lastOutput.variables)) {
                // Add error highlighting for failed widget references
                const formattedValue = widget.lastOutput.success ? 
                    JSON.stringify(value) : 
                    `<span style="text-decoration: underline; color: red;">${JSON.stringify(value)}</span>`;
                vars.set(`output.${key}`, formattedValue);
            }
        }
        
        // Update metadata variables
        vars.set('created', widget.metadata?.created || 'Unknown');
        vars.set('modified', widget.metadata?.modified || 'Unknown');
        vars.set('instance_number', widget.metadata?.instanceNumber || 0);
    }

    /**
     * Attached Note Management Methods
     */
    
    editAttachedNote(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget || !widget.attachedNote) return;
        
        widget.attachedNote.editMode = true;
        this.updateWidgetDisplay(widget);
    }

    saveAttachedNote(widgetId) {
        const widget = this.widgets.get(widgetId);
        const editorEl = document.getElementById(`note-editor-${widgetId}`);
        if (!widget || !editorEl) return;
        
        widget.attachedNote.content = editorEl.value;
        widget.attachedNote.editMode = false;
        widget.metadata.modified = new Date().toISOString();
        
        this.updateWidgetDisplay(widget);
        this.saveBoardToStorage();
        
        // Fire event
        this.fireWidgetEvent(widgetId, 'note_updated', { content: widget.attachedNote.content });
    }

    cancelAttachedNoteEdit(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        widget.attachedNote.editMode = false;
        this.updateWidgetDisplay(widget);
    }

    /**
     * Execute widget with real Python backend
     */
    async executeWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget || !widget.schema) {
            console.error(`Widget ${widgetId} not found or no schema`);
            return;
        }

        // Check if Python is available
        if (!this.pyodide) {
            widget.status = 'error';
            widget.lastOutput = { success: false, error: 'Python environment not available' };
            this.updateWidgetDisplay(widget);
            return;
        }

        // Update widget status and track running widget
        widget.status = 'running';
        this.runningWidgets.add(widgetId);
        this.updateWidgetDisplay(widget);
        
        try {
            // Execute widget with Python backend
            const result = await this.executePythonWidget(widget);
            
            widget.lastOutput = result;
            widget.status = result.success ? 'completed' : 'error';
            
            // Update display
            this.updateWidgetDisplay(widget);
            
            // Fire event triggers
            this.fireWidgetEvent(widgetId, 'output_generated', result);
            
            // Trigger dependent widgets
            this.triggerDependentWidgets(widgetId);
            
            console.log(`Widget ${widgetId} executed:`, result);
            return result;
            
        } catch (error) {
            console.error(`Widget execution failed: ${error}`);
            widget.status = 'error';
            widget.lastOutput = { success: false, error: error.message };
            this.updateWidgetDisplay(widget);
            
            // Fire error event
            this.fireWidgetEvent(widgetId, 'execution_error', { error: error.message });
        } finally {
            // Remove from running widgets
            this.runningWidgets.delete(widgetId);
        }
    }

    /**
     * Execute widget with Python backend
     */
    async executePythonWidget(widget) {
        if (!this.pyodide) {
            return { success: false, error: 'Python environment not available' };
        }

        try {
            // Prepare widget configuration and connections
            const config = widget.config || {};
            const connections = this.getWidgetConnections(widget.id);
            
            // Call Python execution function
            const pythonCall = `execute_widget('${widget.id}', '${widget.type}', ${JSON.stringify(config)}, ${JSON.stringify(connections)})`;
            const result = this.pyodide.runPython(pythonCall);
            
            // Parse result if it's a JSON string
            const parsedResult = typeof result === 'string' ? JSON.parse(result) : result;
            
            return {
                success: parsedResult.success || true,
                result: parsedResult.result,
                stdout: parsedResult.stdout || '',
                stderr: parsedResult.stderr || '',
                variables: parsedResult.variables || {},
                status: parsedResult.status || 'completed',
                execution_time: Date.now() - widget.executionStartTime || 0
            };
            
        } catch (error) {
            console.error('Python execution error:', error);
            return {
                success: false,
                error: error.message,
                traceback: error.stack,
                stdout: '',
                stderr: error.message
            };
        }
    }

    /**
     * Stop widget execution
     */
    async stopWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;

        if (this.runningWidgets.has(widgetId)) {
            // Call Python stop function
            if (this.pyodide) {
                try {
                    this.pyodide.runPython(`stop_widget('${widgetId}')`);
                } catch (error) {
                    console.error('Error stopping widget:', error);
                }
            }
            
            // Update widget status
            widget.status = 'stopped';
            this.runningWidgets.delete(widgetId);
            this.updateWidgetDisplay(widget);
            
            // Fire stop event
            this.fireWidgetEvent(widgetId, 'execution_stopped', {});
            
            console.log(`Widget ${widgetId} stopped`);
        }
    }

    /**
     * Get connections for a widget
     */
    getWidgetConnections(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget || !widget.connections) return {};
        
        const connections = {};
        
        // Input connections
        if (widget.connections.inputs && widget.connections.inputs.size > 0) {
            connections.inputs = {};
            for (const [inputPath, sourceId] of widget.connections.inputs) {
                const sourceWidget = this.widgets.get(sourceId);
                if (sourceWidget && sourceWidget.lastOutput && sourceWidget.lastOutput.success) {
                    connections.inputs[inputPath] = sourceWidget.lastOutput;
                }
            }
        }
        
        return connections;
    }

    /**
     * Event System for Widget Communication
     */
    
    /**
     * Add event listener for widget events
     */
    addEventListener(eventType, widgetId, callback) {
        const key = `${eventType}:${widgetId || '*'}`;
        if (!this.eventListeners.has(key)) {
            this.eventListeners.set(key, []);
        }
        this.eventListeners.get(key).push(callback);
    }

    /**
     * Remove event listener
     */
    removeEventListener(eventType, widgetId, callback) {
        const key = `${eventType}:${widgetId || '*'}`;
        if (this.eventListeners.has(key)) {
            const listeners = this.eventListeners.get(key);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    /**
     * Fire widget event to all listeners
     */
    fireWidgetEvent(widgetId, eventType, data) {
        // Fire for specific widget
        const specificKey = `${eventType}:${widgetId}`;
        if (this.eventListeners.has(specificKey)) {
            this.eventListeners.get(specificKey).forEach(callback => {
                try {
                    callback(widgetId, eventType, data);
                } catch (error) {
                    console.error('Event listener error:', error);
                }
            });
        }

        // Fire for global listeners
        const globalKey = `${eventType}:*`;
        if (this.eventListeners.has(globalKey)) {
            this.eventListeners.get(globalKey).forEach(callback => {
                try {
                    callback(widgetId, eventType, data);
                } catch (error) {
                    console.error('Global event listener error:', error);
                }
            });
        }

        console.log(`Event fired: ${eventType} for widget ${widgetId}`, data);
    }

    /**
     * Generate incremental widget ID based on slug
     */
    generateWidgetId(widgetSchema) {
        const slug = widgetSchema.id || 'widget';
        
        // Get current count for this slug
        const currentCount = this.slugCounters.get(slug) || 0;
        const newCount = currentCount + 1;
        this.slugCounters.set(slug, newCount);
        
        // Generate incremental ID: slug-1, slug-2, etc.
        return `${slug}-${newCount}`;
    }

    /**
     * Cycle Detection for Widget Dependencies
     */
    detectCycles() {
        const visited = new Set();
        const recursionStack = new Set();
        
        // Check all widgets for cycles
        for (const widgetId of this.widgets.keys()) {
            if (this.hasCycleDFS(widgetId, visited, recursionStack)) {
                return true;
            }
        }
        return false;
    }

    /**
     * DFS helper for cycle detection
     */
    hasCycleDFS(widgetId, visited, recursionStack) {
        if (recursionStack.has(widgetId)) {
            return true; // Cycle detected
        }
        
        if (visited.has(widgetId)) {
            return false; // Already processed
        }
        
        visited.add(widgetId);
        recursionStack.add(widgetId);
        
        // Check all widgets that depend on this widget's output
        for (const [targetId, targetWidget] of this.widgets) {
            if (targetWidget.connections && targetWidget.connections.inputs) {
                for (const [inputPath, sourceId] of targetWidget.connections.inputs) {
                    if (sourceId === widgetId) {
                        if (this.hasCycleDFS(targetId, visited, recursionStack)) {
                            return true;
                        }
                    }
                }
            }
        }
        
        recursionStack.delete(widgetId);
        return false;
    }

    /**
     * Connect widgets with cycle detection
     */
    connectWidgetsWithValidation(sourceId, targetId, outputPath, inputPath) {
        // First, add the connection temporarily
        const targetWidget = this.widgets.get(targetId);
        if (!targetWidget.connections) {
            targetWidget.connections = { inputs: new Map(), outputs: new Map() };
        }
        
        const oldInput = targetWidget.connections.inputs.get(inputPath);
        targetWidget.connections.inputs.set(inputPath, sourceId);
        
        // Check for cycles
        if (this.detectCycles()) {
            // Revert the connection
            if (oldInput) {
                targetWidget.connections.inputs.set(inputPath, oldInput);
            } else {
                targetWidget.connections.inputs.delete(inputPath);
            }
            
            throw new Error(`Connection would create a cycle: ${sourceId} → ${targetId}`);
        }
        
        // Update source widget connections
        const sourceWidget = this.widgets.get(sourceId);
        if (!sourceWidget.connections) {
            sourceWidget.connections = { inputs: new Map(), outputs: new Map() };
        }
        
        if (!sourceWidget.connections.outputs.has(outputPath)) {
            sourceWidget.connections.outputs.set(outputPath, []);
        }
        sourceWidget.connections.outputs.get(outputPath).push({
            targetId,
            inputPath
        });
        
        console.log(`Connected ${sourceId}[${outputPath}] → ${targetId}[${inputPath}]`);
        return true;
    }

    /**
     * Enhanced Widget Creation with Proper ID Management
     */
    createWidgetWithId(widgetType, position, widgetSchema) {
        // Generate proper incremental ID
        const widgetId = this.generateWidgetId(widgetSchema);
        
        const widget = {
            id: widgetId,
            type: widgetType,
            schema: widgetSchema,
            position: position,
            config: this.getDefaultConfigFromSchema(widgetSchema),
            status: 'idle',
            lastOutput: null,
            connections: {
                inputs: new Map(),
                outputs: new Map()
            },
            attachedNote: {
                visible: true,
                content: `# Notes for ${widgetSchema.name}\n\nThis widget instance: **${widgetId}**\n\nLast executed: *Never*\n\nConfiguration: {{config}}\n\nLast output: {{output}}`,
                variables: new Map()
            },
            actions: widgetSchema.actions || {},
            executionStartTime: null,
            metadata: {
                slug: widgetSchema.id,
                instanceNumber: this.slugCounters.get(widgetSchema.id),
                created: new Date().toISOString(),
                modified: new Date().toISOString()
            }
        };

        this.widgets.set(widgetId, widget);
        
        // Fire widget created event
        this.fireWidgetEvent(widgetId, 'widget_created', { widget });
        
        console.log(`Created widget: ${widgetId} (${widgetType})`);
        return widget;
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
        
        // Update attached note
        const noteElement = element.querySelector('.widget-attached-note');
        if (noteElement && widget.attachedNote) {
            noteElement.innerHTML = this.renderAttachedNote(widget);
            noteElement.style.display = widget.attachedNote.visible ? 'block' : 'none';
        }
        
        // Update stop button visibility
        const stopButton = element.querySelector('.stop-btn');
        if (stopButton) {
            stopButton.style.display = widget.status === 'running' ? 'inline-block' : 'none';
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

function stopWidget(widgetId) {
    boardApp.stopWidget(widgetId);
}

function toggleAttachedNote(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget || !widget.attachedNote) return;
    
    widget.attachedNote.visible = !widget.attachedNote.visible;
    const noteEl = document.getElementById(`note-${widgetId}`);
    if (noteEl) {
        noteEl.style.display = widget.attachedNote.visible ? 'block' : 'none';
    }
    
    boardApp.saveBoardToStorage();
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
    // Enhanced connection interface with cycle detection
    const sourceId = prompt('Connect FROM widget ID:');
    const outputPath = prompt('Output path (e.g., data.x):') || 'result';
    const inputPath = prompt('Input path (e.g., data):') || 'data';
    
    if (sourceId && sourceId !== widgetId) {
        try {
            boardApp.connectWidgetsWithValidation(sourceId, widgetId, outputPath, inputPath);
            boardApp.updateStatus(`Connected ${sourceId} → ${widgetId}`, 'success');
        } catch (error) {
            boardApp.updateStatus(`Connection failed: ${error.message}`, 'error');
            console.error('Connection error:', error);
        }
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

/**
 * Sticky Note Widget Enhanced Functions
 */
function toggleStickyEditMode(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget || widget.type !== 'sticky-note') return;
    
    const contentEl = document.getElementById(`content-${widgetId}`);
    const isEditing = widget.isEditing || false;
    
    if (!isEditing) {
        // Switch to edit mode
        const currentContent = widget.config.content || '# New Note\n\nEdit to add content...';
        contentEl.innerHTML = `
            <div class="sticky-note-editor">
                <textarea id="editor-${widgetId}" class="markdown-editor">${currentContent}</textarea>
                <div class="editor-toolbar">
                    <button onclick="saveStickyNote('${widgetId}')">💾 Save</button>
                    <button onclick="cancelStickyEdit('${widgetId}')">❌ Cancel</button>
                    <button onclick="previewStickyNote('${widgetId}')">👁️ Preview</button>
                </div>
            </div>
        `;
        widget.isEditing = true;
        
        // Auto-resize textarea
        const textarea = document.getElementById(`editor-${widgetId}`);
        textarea.style.height = (contentEl.clientHeight - 40) + 'px';
    } else {
        // Switch back to view mode
        saveStickyNote(widgetId);
    }
}

function saveStickyNote(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget) return;
    
    const editorEl = document.getElementById(`editor-${widgetId}`);
    if (editorEl) {
        widget.config.content = editorEl.value;
        widget.isEditing = false;
        boardApp.updateWidgetDisplay(widget);
        boardApp.saveBoardToStorage();
    }
}

function cancelStickyEdit(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget) return;
    
    widget.isEditing = false;
    boardApp.updateWidgetDisplay(widget);
}

function previewStickyNote(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    const editorEl = document.getElementById(`editor-${widgetId}`);
    if (!widget || !editorEl) return;
    
    const tempContent = editorEl.value;
    const contentEl = document.getElementById(`content-${widgetId}`);
    contentEl.innerHTML = `
        <div class="sticky-note-preview">
            ${boardApp.renderMarkdown(tempContent)}
            <div class="preview-toolbar">
                <button onclick="toggleStickyEditMode('${widgetId}')">✏️ Back to Edit</button>
            </div>
        </div>
    `;
}

function changeStickyTheme(widgetId, themeName) {
    const widget = boardApp.widgets.get(widgetId);
    const widgetEl = document.querySelector(`[data-widget-id="${widgetId}"]`);
    if (!widget || !widgetEl || widget.type !== 'sticky-note') return;
    
    // Remove existing theme classes
    widgetEl.classList.remove('theme-desert', 'theme-ocean', 'theme-forest', 'theme-sunset');
    
    // Add new theme class
    widgetEl.classList.add(`theme-${themeName}`);
    
    // Update widget config
    widget.config.theme = themeName || 'desert';
    boardApp.saveBoardToStorage();
    
    console.log(`Changed sticky note ${widgetId} theme to ${themeName}`);
}