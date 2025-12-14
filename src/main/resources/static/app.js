const API_BASE = 'http://localhost:8080/api';

const ROLE_CONFIG = {
    child: {
        label: 'Child',
        assigner: null,
        permissions: {
            addTask: false,
            addWish: true,
            completeTask: true,
            rateTask: false,
            approveWish: false
        }
    },
    parent: {
        label: 'Parent',
        assigner: 'P',
        permissions: {
            addTask: true,
            addWish: true,
            completeTask: false,
            rateTask: true,
            approveWish: true
        }
    },
    teacher: {
        label: 'Teacher',
        assigner: 'T',
        permissions: {
            addTask: true,
            addWish: false,
            completeTask: false,
            rateTask: true,
            approveWish: false
        }
    }
};

let currentRole = null;
let cachedTasks = [];
let cachedWishes = [];
let currentCoins = 0;
let currentLevel = 1;

document.addEventListener('DOMContentLoaded', () => {
    initRoleSelection();
    initTabs();
    initFilters();
    initForms();
    lockAppShell(true);
    document.getElementById('change-role-btn').addEventListener('click', showRoleOverlay);
});

function initRoleSelection() {
    const overlay = document.getElementById('role-overlay');
    overlay.classList.add('visible');
    lockAppShell(true);

    document.querySelectorAll('.role-card').forEach(card => {
        card.addEventListener('click', () => {
            setRole(card.dataset.role);
            overlay.classList.remove('visible');
            lockAppShell(false);
        });
    });
}

function showRoleOverlay() {
    document.getElementById('role-overlay').classList.add('visible');
    lockAppShell(true);
    currentRole = null;
}

function setRole(role) {
    if (!ROLE_CONFIG[role]) {
        return;
    }
    currentRole = role;
    document.body.dataset.role = role;

    document.getElementById('role-pill').textContent = `${ROLE_CONFIG[role].label} view`;
    updateRoleVisibility();
    activateDefaultTab();
    refreshData();
}

function lockAppShell(isLocked) {
    const shell = document.querySelector('.app-shell');
    if (shell) {
        shell.classList.toggle('app-shell-locked', isLocked);
    }
    document.body.classList.toggle('prelogin', isLocked);
}

function updateRoleVisibility() {
    document.querySelectorAll('[data-visible-for]').forEach(element => {
        const allowed = element.dataset.visibleFor.split(',').map(item => item.trim());
        element.style.display = allowed.includes(currentRole) ? '' : 'none';
    });
}

function activateDefaultTab() {
    showTab('dashboard');
    document.querySelectorAll('.tab-btn').forEach(btn => {
        const allowed = btn.dataset.visibleFor.split(',').map(item => item.trim());
        btn.style.display = allowed.includes(currentRole) ? '' : 'none';
        btn.classList.remove('active');
    });
    const defaultBtn = document.querySelector('.tab-btn[data-tab="dashboard"]');
    defaultBtn?.classList.add('active');
}

function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            if (!target) {
                return;
            }
            showTab(target);
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (target === 'tasks') {
                loadTasks('all');
            } else if (target === 'wishes') {
                loadWishes();
            }
        });
    });
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    const selected = document.getElementById(`${tabName}-tab`);
    if (selected) {
        selected.classList.add('active');
    }
}

function initFilters() {
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', e => {
            const filter = e.currentTarget.dataset.filter;
            document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            loadTasks(filter);
        });
    });
}

function initForms() {
    const addTaskForm = document.getElementById('add-task-form');
    const addWishForm = document.getElementById('add-wish-form');

    if (addTaskForm) {
        addTaskForm.addEventListener('submit', handleAddTask);
    }
    if (addWishForm) {
        addWishForm.addEventListener('submit', handleAddWish);
    }
}

function refreshData() {
    loadStatus();
    loadTasks('all');
    loadWishes();
}

function loadStatus() {
    fetch(`${API_BASE}/status/budget`)
        .then(res => res.json())
        .then(data => {
            currentCoins = data.budget;
            document.getElementById('budget').textContent = data.budget;
            updateProgressBar();
        })
        .catch(err => console.error('Error loading budget:', err));

    fetch(`${API_BASE}/status/level`)
        .then(res => res.json())
        .then(data => {
            currentLevel = data.level;
            document.getElementById('level').textContent = data.level;
            updateProgressBar();
        })
        .catch(err => console.error('Error loading level:', err));
}

function updateProgressBar() {
    const thresholds = [0, 40, 60, 80, 100];
    const levelIndex = Math.min(currentLevel, thresholds.length - 1);
    const lower = thresholds[levelIndex - 1] || 0;
    const upper = thresholds[levelIndex] || thresholds[thresholds.length - 1];
    const span = Math.max(upper - lower, 1);
    const progress = Math.min(Math.max((currentCoins - lower) / span, 0), 1);

    document.getElementById('points-progress').style.width = `${progress * 100}%`;
    document.getElementById('level-progress-label').textContent = `${Math.round(progress * 100)}%`;
}

function loadTasks(filter) {
    if (!currentRole) {
        return;
    }
    let endpoint = '/tasks/all';
    if (filter === 'daily') endpoint = '/tasks/daily';
    if (filter === 'weekly') endpoint = '/tasks/weekly';

    fetch(`${API_BASE}${endpoint}`)
        .then(res => res.json())
        .then(tasks => {
            cachedTasks = tasks;
            renderTasks(tasks);
            updateDashboard();
        })
        .catch(err => {
            console.error('Error loading tasks:', err);
            document.getElementById('tasks-list').innerHTML = `
                <div class="empty-state">
                    <h3>Unable to load tasks</h3>
                    <p>Please try again in a moment.</p>
                </div>`;
        });
}

function renderTasks(tasks) {
    const tasksList = document.getElementById('tasks-list');
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <h3>No tasks found</h3>
                <p>Add a new task or adjust your filters.</p>
            </div>`;
        return;
    }

    tasksList.innerHTML = tasks.map(task => createTaskCard(task)).join('');

    tasks.forEach(task => {
        const canComplete = ROLE_CONFIG[currentRole].permissions.completeTask && !task.completed;
        const canRate = ROLE_CONFIG[currentRole].permissions.rateTask && task.completed && task.status !== 'Approved';

        if (canComplete) {
            const completeBtn = document.querySelector(`[data-task-id="${task.taskID}"].complete-btn`);
            completeBtn?.addEventListener('click', () => completeTask(task.taskID));
        }
        if (canRate) {
            const checkBtn = document.querySelector(`[data-task-id="${task.taskID}"].check-btn`);
            checkBtn?.addEventListener('click', () => showRatingDialog(task.taskID));
        }
    });
}

function createTaskCard(task) {
    const startDate = formatDate(task.startdate);
    const endDate = formatDate(task.enddate);
    const startTime = task.startTime || '';
    const endTime = task.endTime || '';
    const assignerName = task.assigner === 'T' ? 'Teacher' : 'Parent';

    const canComplete = ROLE_CONFIG[currentRole].permissions.completeTask && !task.completed;
    const canRate = ROLE_CONFIG[currentRole].permissions.rateTask && task.completed && task.status !== 'Approved';

    return `
        <div class="item-card ${task.completed ? 'completed' : ''}">
            <h3>${task.taskTitle}</h3>
            <p>${task.taskDescription}</p>
            <div class="meta">
                <span>ID: ${task.taskID}</span>
                <span>Reward: ${task.coin} coins</span>
                <span>Assigner: ${assignerName}</span>
                ${startDate ? `<span>Starts: ${startDate} ${startTime}</span>` : ''}
                ${endDate ? `<span>Due: ${endDate} ${endTime}</span>` : ''}
                <span>Status: ${task.completed ? 'Completed' : 'Pending'}</span>
            </div>
            <div class="actions">
                ${canComplete ? `<button class="btn btn-success complete-btn" data-task-id="${task.taskID}">Mark complete</button>` : ''}
                ${canRate ? `<button class="btn btn-warning check-btn" data-task-id="${task.taskID}">Review & rate</button>` : ''}
            </div>
        </div>
    `;
}

function completeTask(taskId) {
    fetch(`${API_BASE}/tasks/${taskId}/complete`, { method: 'POST' })
        .then(res => res.json())
        .then(() => {
            showAlert('Task marked as completed.', 'success');
            refreshData();
        })
        .catch(err => {
            console.error('Error completing task:', err);
            showAlert('Unable to mark task as completed.', 'error');
        });
}

function showRatingDialog(taskId) {
    const rating = prompt('Rate this task between 1 and 5:');
    if (!rating || rating < 1 || rating > 5) {
        return;
    }

    fetch(`${API_BASE}/tasks/${taskId}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating: parseInt(rating, 10) })
    })
        .then(res => res.json())
        .then(() => {
            showAlert('Task reviewed successfully.', 'success');
            refreshData();
        })
        .catch(err => {
            console.error('Error rating task:', err);
            showAlert('Unable to submit rating.', 'error');
        });
}

function loadWishes() {
    if (!currentRole) {
        return;
    }
    fetch(`${API_BASE}/wishes/all`)
        .then(res => res.json())
        .then(wishes => {
            cachedWishes = wishes;
            renderWishes(wishes);
            updateDashboard();
        })
        .catch(err => {
            console.error('Error loading wishes:', err);
            document.getElementById('wishes-list').innerHTML = `
                <div class="empty-state">
                    <h3>Unable to load wishes</h3>
                    <p>Please try again.</p>
                </div>`;
        });
}

function renderWishes(wishes) {
    const wishesList = document.getElementById('wishes-list');
    if (!wishes || wishes.length === 0) {
        wishesList.innerHTML = `
            <div class="empty-state">
                <h3>No wishes yet</h3>
                <p>Motivate progress by logging a new wish.</p>
            </div>`;
        return;
    }

    const visibleWishes = currentRole === 'child'
        ? wishes.filter(w => !w.level || w.level <= currentLevel)
        : wishes;

    if (visibleWishes.length === 0) {
        wishesList.innerHTML = `
            <div class="empty-state">
                <h3>Keep leveling up!</h3>
                <p>Wishes unlock once you reach the required level.</p>
            </div>`;
        return;
    }

    wishesList.innerHTML = visibleWishes.map(wish => createWishCard(wish)).join('');

    visibleWishes.forEach(wish => {
        if (ROLE_CONFIG[currentRole].permissions.approveWish && wish.isApproved !== 'APPROVED') {
            const approveBtn = document.querySelector(`[data-wish-id="${wish.wishID}"].approve-btn`);
            const rejectBtn = document.querySelector(`[data-wish-id="${wish.wishID}"].reject-btn`);
            const autoBtn = document.querySelector(`[data-wish-id="${wish.wishID}"].auto-approve-btn`);
            approveBtn?.addEventListener('click', () => checkWish(wish.wishID, 'APPROVED'));
            rejectBtn?.addEventListener('click', () => checkWish(wish.wishID, 'REJECTED'));
            autoBtn?.addEventListener('click', () => scheduleAutoApproval(wish.wishID));
        }
    });
}

function createWishCard(wish) {
    const startDate = formatDate(wish.startdate || wish.startDate);
    const endDate = formatDate(wish.enddate || wish.endDate);
    const statusMap = {
        APPROVED: { text: 'Approved', className: 'approved' },
        REJECTED: { text: 'Rejected', className: 'rejected' },
        PENDING: { text: 'Pending', className: 'pending' },
        WAITING: { text: 'Waiting for level', className: 'waiting' }
    };
    const status = statusMap[wish.isApproved] || statusMap.PENDING;

    const canModify = ROLE_CONFIG[currentRole].permissions.approveWish && wish.isApproved !== 'APPROVED';

    return `
        <div class="item-card ${status.className}">
            <h3>${wish.wishName}</h3>
            <p>${wish.wishDescription}</p>
            <div class="meta">
                <span>ID: ${wish.wishID}</span>
                <span>Status: ${status.text}</span>
                ${wish.level ? `<span>Required level: ${wish.level}</span>` : ''}
                ${startDate ? `<span>Available from: ${startDate} ${wish.startTime || ''}</span>` : ''}
                ${endDate ? `<span>Available until: ${endDate} ${wish.endTime || ''}</span>` : ''}
            </div>
            ${canModify ? `
                <div class="actions">
                    <button class="btn btn-success approve-btn" data-wish-id="${wish.wishID}">Approve now</button>
                    ${wish.isApproved === 'PENDING' ? `<button class="btn btn-danger reject-btn" data-wish-id="${wish.wishID}">Reject</button>` : ''}
                    <button class="btn btn-secondary auto-approve-btn" data-wish-id="${wish.wishID}">Auto approve at level</button>
                </div>` : ''}
        </div>
    `;
}

function scheduleAutoApproval(wishId) {
    const levelInput = prompt('Enter the level (1-4) at which this wish should auto-approve:');
    if (levelInput === null) {
        return;
    }
    const parsed = parseInt(levelInput, 10);
    if (Number.isNaN(parsed) || parsed < 1 || parsed > 4) {
        showAlert('Please enter a level between 1 and 4.', 'error');
        return;
    }
    checkWish(wishId, 'APPROVED', parsed);
}

function checkWish(wishId, status, level = null) {
    fetch(`${API_BASE}/wishes/${wishId}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, level })
    })
        .then(res => res.json())
        .then(data => {
            const message = data.message || `Wish ${status === 'APPROVED' ? 'updated' : 'rejected'}.`;
            showAlert(message, 'success');
            refreshData();
        })
        .catch(err => {
            console.error('Error checking wish:', err);
            showAlert('Unable to update wish status.', 'error');
        });
}

function handleAddTask(e) {
    e.preventDefault();
    if (!ROLE_CONFIG[currentRole].permissions.addTask) {
        showAlert('Only parents or teachers can add tasks.', 'error');
        return;
    }

    const taskData = {
        assigner: ROLE_CONFIG[currentRole].assigner,
        taskId: parseInt(document.getElementById('task-id').value, 10),
        taskTitle: document.getElementById('task-title').value,
        taskDescription: document.getElementById('task-description').value,
        startDate: document.getElementById('task-start-date').value || null,
        startTime: document.getElementById('task-start-time').value || null,
        endDate: document.getElementById('task-end-date').value || null,
        endTime: document.getElementById('task-end-time').value || null,
        coin: parseInt(document.getElementById('task-coin').value, 10)
    };

    fetch(`${API_BASE}/tasks/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
    })
        .then(res => res.json())
        .then(() => {
            showAlert('Task added successfully.', 'success');
            document.getElementById('add-task-form').reset();
            refreshData();
        })
        .catch(err => {
            console.error('Error adding task:', err);
            showAlert('Unable to add task.', 'error');
        });
}

function handleAddWish(e) {
    e.preventDefault();
    if (!ROLE_CONFIG[currentRole].permissions.addWish) {
        showAlert('This role cannot add wishes.', 'error');
        return;
    }

    const wishData = {
        wishId: document.getElementById('wish-id').value,
        wishTitle: document.getElementById('wish-title').value,
        wishDescription: document.getElementById('wish-description').value,
        startDate: document.getElementById('wish-start-date').value || null,
        startTime: document.getElementById('wish-start-time').value || null,
        endDate: document.getElementById('wish-end-date').value || null,
        endTime: document.getElementById('wish-end-time').value || null
    };

    fetch(`${API_BASE}/wishes/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wishData)
    })
        .then(res => res.json())
        .then(() => {
            showAlert('Wish submitted for review.', 'success');
            document.getElementById('add-wish-form').reset();
            refreshData();
        })
        .catch(err => {
            console.error('Error adding wish:', err);
            showAlert('Unable to add wish.', 'error');
        });
}

function updateDashboard() {
    const totalTasks = cachedTasks.length;
    const completedTasks = cachedTasks.filter(t => t.completed).length;
    const awaitingReview = cachedTasks.filter(t => t.completed && t.status !== 'Approved').length;

    const dailyTasks = cachedTasks.filter(task => isWithinRange(task.enddate, 'daily')).length;
    const weeklyTasks = cachedTasks.filter(task => isWithinRange(task.enddate, 'weekly')).length;

    const activeWishes = cachedWishes.length;
    const pendingWishes = cachedWishes.filter(w => w.isApproved === 'PENDING' || w.isApproved === 'WAITING').length;
    const eligibleWishes = cachedWishes.filter(w => !w.level || w.level <= currentLevel).length;

    document.getElementById('metric-total-tasks').textContent = totalTasks;
    document.getElementById('metric-completed-tasks').textContent = completedTasks;
    document.getElementById('metric-completion-rate').textContent = totalTasks === 0 ? '0%' : `${Math.round((completedTasks / totalTasks) * 100)}%`;

    document.getElementById('metric-daily-tasks').textContent = dailyTasks;
    document.getElementById('metric-weekly-tasks').textContent = weeklyTasks;
    document.getElementById('metric-awaiting-review').textContent = awaitingReview;

    document.getElementById('metric-active-wishes').textContent = activeWishes;
    document.getElementById('metric-pending-wishes').textContent = pendingWishes;
    document.getElementById('metric-eligible-wishes').textContent = eligibleWishes;
}

function isWithinRange(dateValue, range) {
    if (!dateValue) return false;
    const date = new Date(formatDate(dateValue, true));
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (range === 'daily') {
        return date.getTime() === today.getTime();
    }

    if (range === 'weekly') {
        const day = today.getDay();
        const diffToMonday = day === 0 ? 6 : day - 1;
        const monday = new Date(today);
        monday.setDate(today.getDate() - diffToMonday);
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        return date >= monday && date <= sunday;
    }
    return false;
}

function formatDate(dateValue, raw = false) {
    if (!dateValue) return '';
    try {
        const dateStr = Array.isArray(dateValue)
            ? `${dateValue[0]}-${String(dateValue[1]).padStart(2, '0')}-${String(dateValue[2]).padStart(2, '0')}`
            : dateValue;
        if (raw) {
            return dateStr;
        }
        return new Date(`${dateStr}T00:00:00`).toLocaleDateString('en-GB');
    } catch (e) {
        return Array.isArray(dateValue) ? dateValue.join('-') : dateValue;
    }
}

function showAlert(message, type) {
    const alert = document.querySelector('.alert');
    if (!alert) {
        return;
    }
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    setTimeout(() => alert.classList.remove('show'), 3200);
}
