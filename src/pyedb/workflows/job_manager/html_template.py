# HTML template for the web dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyEDB Solver Manager</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            font-size: 14px;
            color: #6c757d;
        }
        .resource-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        .resource-bar {
            height: 20px;
            background-color: #e9ecef;
            border-radius: 4px;
            margin-bottom: 8px;
            overflow: hidden;
        }
        .resource-fill {
            height: 100%;
            border-radius: 4px;
        }
        .cpu-fill { background-color: #007bff; }
        .memory-fill { background-color: #28a745; }
        .task-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .task-table th, .task-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .task-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .task-table tr:hover {
            background-color: #f5f5f5;
        }
        .status-pending { color: #ffc107; }
        .status-running { color: #17a2b8; }
        .status-completed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-cancelled { color: #6c757d; }
        .progress-bar {
            width: 100%;
            background-color: #e9ecef;
            border-radius: 4px;
            height: 8px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            background-color: #007bff;
        }
        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-cancel { background-color: #dc3545; color: white; }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .filter-bar {
            margin-bottom: 20px;
        }
        .filter-select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ced4da;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PyEDB Solver Manager</h1>

        <div class="dashboard">
            <div class="stats" id="stats">
                <!-- Stats will be populated by JavaScript -->
            </div>

            <div class="resource-card">
                <h3>System Resources</h3>
                <div id="resource-info">
                    <!-- Resource info will be populated by JavaScript -->
                </div>
            </div>
        </div>

        <div class="filter-bar">
            <label for="status-filter">Filter by status:</label>
            <select id="status-filter" class="filter-select" onchange="loadTasks()">
                <option value="">All</option>
                <option value="Pending">Pending</option>
                <option value="Running">Running</option>
                <option value="Completed">Completed</option>
                <option value="Failed">Failed</option>
                <option value="Cancelled">Cancelled</option>
            </select>
        </div>

        <h2>Simulation Tasks</h2>
        <table class="task-table" id="task-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Project</th>
                    <th>Solver</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Cores</th>
                    <th>Memory (GB)</th>
                    <th>Priority</th>
                    <th>Created</th>
                    <th>Started</th>
                    <th>Duration</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <!-- Tasks will be populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <script>
        let refreshInterval;

        function formatDate(dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleString();
        }

        function formatDuration(start, end) {
            if (!start) return '-';
            const startDate = new Date(start);
            const endDate = end ? new Date(end) : new Date();
            const seconds = Math.floor((endDate - startDate) / 1000);

            if (seconds < 60) return `${seconds}s`;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            if (minutes < 60) return `${minutes}m ${remainingSeconds}s`;
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            return `${hours}h ${remainingMinutes}m`;
        }

        function updateStats(stats) {
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${stats.pending_tasks}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.running_tasks}</div>
                    <div class="stat-label">Running</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.completed_tasks}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.tasks_failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.tasks_cancelled}</div>
                    <div class="stat-label">Cancelled</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Math.floor(stats.uptime / 3600)}h ${Math.floor((stats.uptime % 3600) /
                    60)}m</div>
                    <div class="stat-label">Uptime</div>
                </div>
            `;

            const resourceDiv = document.getElementById('resource-info');
            const cpuPercent = Math.min(100, Math.round(stats.allocated_cores / stats.total_cores * 100));
            const memoryPercent = Math.min(100, Math.round((stats.total_memory_gb - stats.available_memory_gb) /
            stats.total_memory_gb * 100));

            resourceDiv.innerHTML = `
                <div>
                    <strong>CPU:</strong> ${stats.allocated_cores}/${stats.total_cores} cores (${cpuPercent}%)
                    <div class="resource-bar">
                        <div class="resource-fill cpu-fill" style="width: ${cpuPercent}%"></div>
                    </div>
                </div>
                <div>
                    <strong>Memory:</strong> ${(stats.total_memory_gb - stats.available_memory_gb).toFixed(1)}/
                    ${stats.total_memory_gb.toFixed(1)} GB (${memoryPercent}%)
                    <div class="resource-bar">
                        <div class="resource-fill memory-fill" style="width: ${memoryPercent}%"></div>
                    </div>
                </div>
                <div><strong>Available Cores:</strong> ${stats.available_cores}</div>
                <div><strong>Available Memory:</strong> ${stats.available_memory_gb.toFixed(1)} GB</div>
            `;
        }

        function loadTasks() {
            const statusFilter = document.getElementById('status-filter').value;
            let url = '/api/tasks';
            if (statusFilter) {
                url += `?status=${statusFilter}`;
            }

            fetch(url)
                .then(response => response.json())
                .then(tasks => {
                    const tbody = document.querySelector('#task-table tbody');
                    tbody.innerHTML = '';

                    tasks.forEach(task => {
                        const row = document.createElement('tr');

                        // Progress bar
                        const progressBar = task.progress ? `
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${task.progress}%"></div>
                            </div>
                            ${task.progress.toFixed(1)}%
                        ` : '-';

                        // Memory info
                        const memoryInfo = task.peak_memory_used_gb ?
                            `${task.peak_memory_used_gb.toFixed(1)}/${task.resource_reqs.estimated_memory_gb}` :
                            `${task.resource_reqs.min_memory_gb}/${task.resource_reqs.estimated_memory_gb}`;

                        // Actions
                        let actions = '';
                        if (task.status === 'Pending' || task.status === 'Running') {
                            actions = `
                                <button class="btn btn-cancel" onclick="cancelTask('${task.task_id}')">Cancel</button>
                                ${task.status === 'Pending' ? `
                                    <select onchange="setPriority('${task.task_id}', this.value)">
                                        ${Array.from({length: 10}, (_, i) => i + 1).map(p => `
                                            <option value="${p}" ${p === task.priority ? 'selected' : ''}>${p}</option>
                                        `).join('')}
                                    </select>
                                ` : ''}
                            `;
                        } else {
                            actions = '-';
                        }

                        row.innerHTML = `
                            <td>${task.task_id}</td>
                            <td>${task.project_name}</td>
                            <td>${task.solver_type}</td>
                            <td class="status-${task.status.toLowerCase()}">${task.status}</td>
                            <td>${progressBar}</td>
                            <td>${task.resource_reqs.min_cores}${task.actual_cores_used ? ` (${task.actual_cores_used})`
                             : ''}</td>
                            <td>${memoryInfo} GB</td>
                            <td>${task.priority}</td>
                            <td>${formatDate(task.created_time)}</td>
                            <td>${formatDate(task.start_time)}</td>
                            <td>${formatDuration(task.start_time, task.end_time)}</td>
                            <td>${actions}</td>
                        `;

                        tbody.appendChild(row);
                    });
                });
        }

        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(stats => {
                    updateStats(stats);
                });
        }

        function cancelTask(taskId) {
            fetch(`/api/cancel/${taskId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadTasks();
                        loadStats();
                    } else {
                        alert('Failed to cancel task');
                    }
                });
        }

        function setPriority(taskId, priority) {
            fetch(`/api/priority/${taskId}/${priority}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        alert('Failed to set priority');
                    }
                });
        }

        // Initial load
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadTasks();

            // Refresh every 5 seconds
            refreshInterval = setInterval(() => {
                loadStats();
                loadTasks();
            }, 5000);
        });

        // Clean up on page unload
        window.addEventListener('beforeunload', function() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        });
    </script>
</body>
</html>
"""
