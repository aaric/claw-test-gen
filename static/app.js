// API base URL
const API_BASE = '/api/todos';

// State
let todos = [];
let currentFilter = 'all';

// DOM elements
const todoForm = document.getElementById('todo-form');
const todoTitle = document.getElementById('todo-title');
const todoDescription = document.getElementById('todo-description');
const todoPriority = document.getElementById('todo-priority');
const todoList = document.getElementById('todo-list');
const emptyState = document.getElementById('empty-state');
const todoCount = document.getElementById('todo-count');
const filterButtons = document.querySelectorAll('.filter-btn');
const clearCompletedBtn = document.getElementById('clear-completed');
const notification = document.getElementById('notification');

// API functions
async function fetchTodos() {
    const response = await fetch(API_BASE);
    if (!response.ok) throw new Error('Failed to fetch todos');
    return response.json();
}

async function createTodo(data) {
    const response = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create todo');
    return response.json();
}

async function updateTodo(id, data) {
    const response = await fetch(`${API_BASE}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update todo');
    return response.json();
}

async function toggleTodo(id) {
    const response = await fetch(`${API_BASE}/${id}/toggle`, {
        method: 'PATCH'
    });
    if (!response.ok) throw new Error('Failed to toggle todo');
    return response.json();
}

async function deleteTodo(id) {
    const response = await fetch(`${API_BASE}/${id}`, {
        method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete todo');
}

async function clearCompleted() {
    const completedTodos = todos.filter(t => t.completed);
    await Promise.all(completedTodos.map(t => deleteTodo(t.id)));
}

// UI functions
function renderTodos() {
    const filteredTodos = todos.filter(todo => {
        if (currentFilter === 'active') return !todo.completed;
        if (currentFilter === 'completed') return todo.completed;
        return true;
    });

    if (filteredTodos.length === 0) {
        todoList.innerHTML = '';
        emptyState.classList.remove('hidden');
    } else {
        emptyState.classList.add('hidden');
        todoList.innerHTML = filteredTodos.map(todo => createTodoHTML(todo)).join('');
    }

    updateCount();
    attachEventListeners();
}

function createTodoHTML(todo) {
    const date = new Date(todo.created_at).toLocaleDateString();
    return `
        <div class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
            <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
            <div class="todo-content">
                <div class="todo-title">${escapeHTML(todo.title)}</div>
                ${todo.description ? `<div class="todo-description">${escapeHTML(todo.description)}</div>` : ''}
                <div class="todo-meta">
                    <span class="todo-priority ${todo.priority}">${todo.priority}</span>
                    <span class="todo-date">${date}</span>
                </div>
            </div>
            <div class="todo-actions">
                <button class="btn-icon btn-edit" title="Edit">✏️</button>
                <button class="btn-icon btn-delete" title="Delete">🗑️</button>
            </div>
        </div>
    `;
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function updateCount() {
    const activeCount = todos.filter(t => !t.completed).length;
    todoCount.textContent = `${activeCount} item${activeCount !== 1 ? 's' : ''} remaining`;
}

function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}

function attachEventListeners() {
    // Checkbox toggle
    document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', async (e) => {
            const id = e.target.closest('.todo-item').dataset.id;
            try {
                const updated = await toggleTodo(id);
                todos = todos.map(t => t.id === id ? updated : t);
                renderTodos();
            } catch (err) {
                showNotification(err.message, 'error');
            }
        });
    });

    // Delete buttons
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.closest('.todo-item').dataset.id;
            try {
                await deleteTodo(id);
                todos = todos.filter(t => t.id !== id);
                renderTodos();
                showNotification('Todo deleted');
            } catch (err) {
                showNotification(err.message, 'error');
            }
        });
    });

    // Edit buttons
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.closest('.todo-item').dataset.id;
            openEditModal(id);
        });
    });
}

// Edit modal
function openEditModal(id) {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const modal = document.createElement('div');
    modal.className = 'edit-modal active';
    modal.innerHTML = `
        <div class="edit-modal-content">
            <h2>Edit Todo</h2>
            <div class="edit-form-group">
                <label>Title</label>
                <input type="text" id="edit-title" value="${escapeHTML(todo.title)}" maxlength="200">
            </div>
            <div class="edit-form-group">
                <label>Description</label>
                <textarea id="edit-description" rows="3" maxlength="1000">${escapeHTML(todo.description || '')}</textarea>
            </div>
            <div class="edit-form-group">
                <label>Priority</label>
                <select id="edit-priority">
                    <option value="low" ${todo.priority === 'low' ? 'selected' : ''}>Low</option>
                    <option value="medium" ${todo.priority === 'medium' ? 'selected' : ''}>Medium</option>
                    <option value="high" ${todo.priority === 'high' ? 'selected' : ''}>High</option>
                </select>
            </div>
            <div class="edit-modal-buttons">
                <button class="btn-cancel">Cancel</button>
                <button class="btn-save">Save</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector('.btn-save').addEventListener('click', async () => {
        const title = document.getElementById('edit-title').value.trim();
        if (!title) {
            showNotification('Title is required', 'error');
            return;
        }

        const data = {
            title,
            description: document.getElementById('edit-description').value.trim() || null,
            priority: document.getElementById('edit-priority').value
        };

        try {
            const updated = await updateTodo(id, data);
            todos = todos.map(t => t.id === id ? updated : t);
            renderTodos();
            document.body.removeChild(modal);
            showNotification('Todo updated');
        } catch (err) {
            showNotification(err.message, 'error');
        }
    });

    modal.querySelector('.btn-cancel').addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Event listeners
todoForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = todoTitle.value.trim();
    if (!title) {
        showNotification('Please enter a title', 'error');
        return;
    }

    const data = {
        title,
        description: todoDescription.value.trim() || null,
        priority: todoPriority.value
    };

    try {
        const newTodo = await createTodo(data);
        todos.push(newTodo);
        renderTodos();
        todoTitle.value = '';
        todoDescription.value = '';
        todoPriority.value = 'medium';
        showNotification('Todo added');
    } catch (err) {
        showNotification(err.message, 'error');
    }
});

filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderTodos();
    });
});

clearCompletedBtn.addEventListener('click', async () => {
    const completedCount = todos.filter(t => t.completed).length;
    if (completedCount === 0) {
        showNotification('No completed todos to clear', 'error');
        return;
    }

    try {
        await clearCompleted();
        todos = todos.filter(t => !t.completed);
        renderTodos();
        showNotification(`${completedCount} todo${completedCount !== 1 ? 's' : ''} cleared`);
    } catch (err) {
        showNotification(err.message, 'error');
    }
});

// Initialize
async function init() {
    try {
        todos = await fetchTodos();
        renderTodos();
    } catch (err) {
        showNotification('Failed to load todos', 'error');
    }
}

init();
