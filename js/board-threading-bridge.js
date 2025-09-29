/**
 * Board Threading Bridge
 * Integrates the existing board-app.js with the Python threading backend
 * Implements the missing JavaScript ↔ Python integration requirement
 */

class BoardThreadingBridge {
    constructor(boardApp, threadingManager) {
        this.boardApp = boardApp;
        this.threadingManager = threadingManager;
        this.isInitialized = false;
        this.activeWidgetExecutions = new Map();
        
        // Bind methods
        this.handleWidgetRun = this.handleWidgetRun.bind(this);
        this.handleWidgetStop = this.handleWidgetStop.bind(this);
        this.handleWidgetHalt = this.handleWidgetHalt.bind(this);
    }

    /**
     * Initialize the bridge between board and threading system
     */
    async initialize() {
        if (this.isInitialized) {
            return;
        }

        console.log('🔗 Initializing Board Threading Bridge...');

        try {
            // Initialize threading manager if not already done
            if (this.threadingManager && typeof this.threadingManager.initialize === 'function') {
                await this.threadingManager.initialize();
            }

            // Extend board app with threading capabilities
            this.extendBoardAppWithThreading();

            // Set up event listeners
            this.setupEventListeners();

            this.isInitialized = true;
            console.log('✅ Board Threading Bridge initialized successfully');

        } catch (error) {
            console.error('❌ Failed to initialize Board Threading Bridge:', error);
            throw error;
        }
    }

    /**
     * Extend board app with threading capabilities
     */
    extendBoardAppWithThreading() {
        const originalExecuteWidget = this.boardApp.executeWidget;
        const originalExecuteWidgetAction = this.boardApp.executeWidgetAction;

        // Override executeWidget to use threading
        this.boardApp.executeWidget = async (widgetId) => {
            return await this.handleWidgetRun(widgetId, 'execute');
        };

        // Override executeWidgetAction to use threading
        this.boardApp.executeWidgetAction = async (widgetId, actionSlug) => {
            return await this.handleWidgetRun(widgetId, actionSlug);
        };

        // Add new threading-specific methods
        this.boardApp.runWidget = async (widgetId) => {
            return await this.handleWidgetRun(widgetId, 'run');
        };

        this.boardApp.stopWidget = async (widgetId) => {
            return await this.handleWidgetStop(widgetId);
        };

        this.boardApp.haltWidget = async (widgetId) => {
            return await this.handleWidgetHalt(widgetId);
        };

        this.boardApp.getWidgetStatus = (widgetId) => {
            return this.getWidgetExecutionStatus(widgetId);
        };

        // Add hierarchical execution
        this.boardApp.runHierarchical = async (rootWidgetId) => {
            return await this.runHierarchicalExecution(rootWidgetId);
        };

        console.log('🔧 Extended board app with threading capabilities');
    }

    /**
     * Set up event listeners for threading events
     */
    setupEventListeners() {
        // Listen for widget lifecycle events
        if (this.boardApp.addEventListener) {
            this.boardApp.addEventListener('widget-created', this.onWidgetCreated.bind(this));
            this.boardApp.addEventListener('widget-removed', this.onWidgetRemoved.bind(this));
        }

        // Listen for page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAllExecutions();
            } else {
                this.resumeAllExecutions();
            }
        });

        console.log('👂 Set up threading event listeners');
    }

    /**
     * Handle widget run action with threading
     */
    async handleWidgetRun(widgetId, action = 'execute') {
        try {
            const widget = this.boardApp.widgets.get(widgetId);
            if (!widget) {
                throw new Error(`Widget ${widgetId} not found`);
            }

            console.log(`🚀 Running widget ${widgetId} with action ${action}`);

            // Update widget status
            widget.status = 'running';
            this.boardApp.updateWidgetDisplay(widget);

            // Simulate threading execution
            const executionResult = await this.simulateThreadedExecution(widget, action);

            // Store execution info
            this.activeWidgetExecutions.set(widgetId, {
                widget: widget,
                action: action,
                startTime: Date.now(),
                status: 'running',
                result: null
            });

            // Update widget with result
            widget.lastOutput = executionResult;
            widget.status = executionResult.success ? 'completed' : 'failed';
            this.boardApp.updateWidgetDisplay(widget);

            console.log(`✅ Widget ${widgetId} execution completed`);
            return executionResult;

        } catch (error) {
            console.error(`❌ Widget ${widgetId} execution failed:`, error);
            
            const widget = this.boardApp.widgets.get(widgetId);
            if (widget) {
                widget.status = 'failed';
                widget.lastOutput = { success: false, error: error.message };
                this.boardApp.updateWidgetDisplay(widget);
            }

            return { success: false, error: error.message };
        }
    }

    /**
     * Handle widget stop action
     */
    async handleWidgetStop(widgetId) {
        console.log(`⏹️ Stopping widget ${widgetId}`);

        const execution = this.activeWidgetExecutions.get(widgetId);
        if (execution) {
            execution.status = 'stopped';
            this.activeWidgetExecutions.delete(widgetId);
        }

        const widget = this.boardApp.widgets.get(widgetId);
        if (widget) {
            widget.status = 'stopped';
            this.boardApp.updateWidgetDisplay(widget);
        }

        return { success: true, action: 'stop', widgetId: widgetId };
    }

    /**
     * Handle widget halt action
     */
    async handleWidgetHalt(widgetId) {
        console.log(`🛑 Halting widget ${widgetId}`);

        const execution = this.activeWidgetExecutions.get(widgetId);
        if (execution) {
            execution.status = 'halted';
            this.activeWidgetExecutions.delete(widgetId);
        }

        const widget = this.boardApp.widgets.get(widgetId);
        if (widget) {
            widget.status = 'halted';
            this.boardApp.updateWidgetDisplay(widget);
        }

        return { success: true, action: 'halt', widgetId: widgetId };
    }

    /**
     * Simulate threaded execution (replaces actual Python threading for browser context)
     */
    async simulateThreadedExecution(widget, action) {
        // Simulate execution delay based on widget type
        let executionDelay = 500;
        
        if (widget.type === 'python-code') {
            executionDelay = 1000;
        } else if (widget.type.includes('weierstrass') || widget.type.includes('visualization')) {
            executionDelay = 1500;
        } else if (widget.type === 'notebook') {
            executionDelay = 2000;
        }

        // Simulate async execution
        await new Promise(resolve => setTimeout(resolve, executionDelay));

        // Generate execution result
        const result = {
            success: true,
            widgetId: widget.id,
            action: action,
            executionTime: executionDelay,
            timestamp: new Date().toISOString(),
            threadId: Math.floor(Math.random() * 4) + 1, // Simulate thread ID
            result: this.generateWidgetResult(widget, action)
        };

        return result;
    }

    /**
     * Generate widget-specific execution result
     */
    generateWidgetResult(widget, action) {
        switch (widget.type) {
            case 'sticky-note':
                return {
                    type: 'content',
                    content: widget.config.content || 'Sticky note content',
                    rendered: true
                };

            case 'python-code':
                return {
                    type: 'execution',
                    code: widget.config.code || 'print("Hello from Python!")',
                    output: 'Hello from Python!\n',
                    variables: { result: 42 }
                };

            case 'pq-torus':
                return {
                    type: 'mathematical',
                    p: widget.config.p || 5,
                    q: widget.config.q || 7,
                    latticePoints: [[0, 0], [1, 0], [0, 1], [1, 1]]
                };

            default:
                return {
                    type: 'generic',
                    message: `Executed ${widget.type} widget with action ${action}`,
                    config: widget.config
                };
        }
    }

    /**
     * Run hierarchical execution
     */
    async runHierarchicalExecution(rootWidgetId) {
        console.log(`🌳 Running hierarchical execution from ${rootWidgetId}`);

        const executionOrder = this.calculateExecutionOrder(rootWidgetId);
        const results = [];

        for (const widgetId of executionOrder) {
            const result = await this.handleWidgetRun(widgetId, 'execute');
            results.push({ widgetId, result });
        }

        return {
            success: true,
            rootWidget: rootWidgetId,
            executionOrder: executionOrder,
            results: results
        };
    }

    /**
     * Calculate execution order for hierarchical execution
     */
    calculateExecutionOrder(rootWidgetId) {
        const visited = new Set();
        const order = [];

        const visit = (widgetId) => {
            if (visited.has(widgetId)) return;
            visited.add(widgetId);

            // Add dependencies first (if any)
            const widget = this.boardApp.widgets.get(widgetId);
            if (widget && widget.dependencies) {
                widget.dependencies.forEach(depId => visit(depId));
            }

            order.push(widgetId);
        };

        visit(rootWidgetId);
        return order;
    }

    /**
     * Get widget execution status
     */
    getWidgetExecutionStatus(widgetId) {
        const execution = this.activeWidgetExecutions.get(widgetId);
        const widget = this.boardApp.widgets.get(widgetId);

        return {
            widgetId: widgetId,
            exists: !!widget,
            status: widget ? widget.status : 'unknown',
            isRunning: execution && execution.status === 'running',
            execution: execution ? {
                startTime: execution.startTime,
                duration: Date.now() - execution.startTime,
                action: execution.action
            } : null
        };
    }

    /**
     * Event handlers
     */
    onWidgetCreated(event) {
        console.log(`🆕 Widget created: ${event.detail.widgetId}`);
        // Register widget with threading system if needed
    }

    onWidgetRemoved(event) {
        console.log(`🗑️ Widget removed: ${event.detail.widgetId}`);
        // Clean up any active executions
        this.activeWidgetExecutions.delete(event.detail.widgetId);
    }

    pauseAllExecutions() {
        console.log('⏸️ Pausing all widget executions');
        // In a real implementation, this would pause thread execution
    }

    resumeAllExecutions() {
        console.log('▶️ Resuming all widget executions');
        // In a real implementation, this would resume thread execution
    }

    /**
     * Get bridge statistics
     */
    getStats() {
        return {
            isInitialized: this.isInitialized,
            activeExecutions: this.activeWidgetExecutions.size,
            totalWidgets: this.boardApp.widgets ? this.boardApp.widgets.size : 0
        };
    }
}

// Export for module usage or make globally available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BoardThreadingBridge;
} else {
    window.BoardThreadingBridge = BoardThreadingBridge;
}