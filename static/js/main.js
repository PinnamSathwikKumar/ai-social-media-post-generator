/**
 * AI Social Media Post Generator - Main JavaScript
 * Handles all frontend functionality including API calls, theme management, and UI interactions
 */

// Global variables
let currentPostId = null;
let currentEventId = null;

// ==================== Theme Management ====================

/**
 * Toggle between dark and light theme
 */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    const themeIcon = document.getElementById('theme-icon');
    if (newTheme === 'light') {
        themeIcon.className = 'fas fa-sun';
    } else {
        themeIcon.className = 'fas fa-moon';
    }
}

/**
 * Load saved theme from localStorage
 */
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const html = document.documentElement;
    html.setAttribute('data-theme', savedTheme);
    
    // Update icon
    const themeIcon = document.getElementById('theme-icon');
    if (savedTheme === 'light') {
        themeIcon.className = 'fas fa-sun';
    } else {
        themeIcon.className = 'fas fa-moon';
    }
}

// ==================== Tab Management ====================

/**
 * Switch between tabs
 * @param {string} tab - Tab name to switch to
 * @param {HTMLElement} button - Button element that triggered the switch
 */
function switchTab(tab, button) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tab + '-tab').classList.add('active');
    if (button) {
        button.classList.add('active');
    }

    if (tab === 'generate') {
        loadEventsForSelect();
    } else if (tab === 'posts') {
        loadEventsForFilter();
        loadPosts();
    }
}

// ==================== Alert System ====================

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, etc.)
 */
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

// ==================== Event Management ====================

/**
 * Load all events and display them
 */
async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        
        if (data.success) {
            const eventsList = document.getElementById('eventsList');
            if (data.events.length === 0) {
                eventsList.innerHTML = '<p class="text-white-50">No events yet. Create your first event!</p>';
                return;
            }
            
            eventsList.innerHTML = data.events.map(event => `
                <div class="event-card">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5>${event.title}</h5>
                            <p class="mb-1"><i class="fas fa-calendar icon"></i>${event.date}</p>
                            ${event.location ? `<p class="mb-1"><i class="fas fa-map-marker-alt icon"></i>${event.location}</p>` : ''}
                            ${event.type ? `<p class="mb-1"><i class="fas fa-tag icon"></i>${event.type}</p>` : ''}
                            ${event.description ? `<p class="mt-2">${event.description}</p>` : ''}
                        </div>
                        <div>
                            <button class="btn btn-danger btn-sm" onclick="deleteEvent(${event.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showAlert('Error loading events: ' + error.message, 'danger');
    }
}

/**
 * Load events for select dropdown (Generate Posts tab)
 */
async function loadEventsForSelect() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('selectEvent');
            select.innerHTML = '<option value="">Choose an event...</option>' + 
                data.events.map(event => 
                    `<option value="${event.id}">${event.title} - ${event.date}</option>`
                ).join('');
        }
    } catch (error) {
        showAlert('Error loading events: ' + error.message, 'danger');
    }
}

/**
 * Load events for filter dropdown (View Posts tab)
 */
async function loadEventsForFilter() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('filterEvent');
            select.innerHTML = '<option value="">All Events</option>' + 
                data.events.map(event => 
                    `<option value="${event.id}">${event.title}</option>`
                ).join('');
        }
    } catch (error) {
        showAlert('Error loading events: ' + error.message, 'danger');
    }
}

/**
 * Delete an event
 * @param {number} eventId - Event ID to delete
 */
async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) return;

    try {
        const response = await fetch(`/api/events/${eventId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert('Event deleted successfully!');
            loadEvents();
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error deleting event: ' + error.message, 'danger');
    }
}

// ==================== Post Generation ====================

/**
 * Generate a social media post
 */
async function generatePost() {
    const eventId = document.getElementById('selectEvent').value;
    const platform = document.getElementById('selectPlatform').value;
    const tone = document.getElementById('selectTone').value;

    if (!eventId) {
        showAlert('Please select an event', 'danger');
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('previewSection').style.display = 'none';
    currentEventId = eventId;

    try {
        const response = await fetch('/api/generate-post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_id: parseInt(eventId),
                platform: platform,
                tone: tone
            })
        });

        const data = await response.json();
        document.getElementById('loading').style.display = 'none';
        
        if (data.success) {
            currentPostId = data.post_id;
            document.getElementById('previewContent').textContent = data.content;
            document.getElementById('previewHashtags').textContent = data.hashtags;
            document.getElementById('previewSection').style.display = 'block';
            showAlert('Post generated successfully!');
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        showAlert('Error generating post: ' + error.message, 'danger');
    }
}

/**
 * Regenerate the current post
 */
function regeneratePost() {
    if (currentEventId) {
        document.getElementById('selectEvent').value = currentEventId;
        generatePost();
    }
}

/**
 * Update post status
 * @param {string} status - New status (approved/posted)
 */
async function updatePostStatus(status) {
    if (!currentPostId) {
        showAlert('No post to update', 'danger');
        return;
    }

    try {
        const response = await fetch(`/api/posts/${currentPostId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(`Post status updated to ${status}!`);
            if (status === 'approved') {
                loadPosts();
            }
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error updating status: ' + error.message, 'danger');
    }
}

// ==================== Post Management ====================

/**
 * Load all generated posts
 */
async function loadPosts() {
    try {
        const eventId = document.getElementById('filterEvent').value;
        const url = eventId ? `/api/posts?event_id=${eventId}` : '/api/posts';
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            const postsList = document.getElementById('postsList');
            if (data.posts.length === 0) {
                postsList.innerHTML = '<p class="text-white-50">No posts generated yet.</p>';
                return;
            }
            
            postsList.innerHTML = data.posts.map(post => `
                <div class="event-card">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h5>${post.event_title}</h5>
                            <span class="status-badge status-${post.status}">${post.status.toUpperCase()}</span>
                            <span class="badge bg-info ms-2">${post.platform}</span>
                            <span class="badge bg-secondary ms-2">${post.tone}</span>
                        </div>
                        <div>
                            <button class="btn btn-danger btn-sm" onclick="deletePost(${post.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="preview-box mb-2">${post.content}</div>
                    <div class="hashtags-box">${post.hashtags || 'No hashtags'}</div>
                    <div class="mt-2">
                        ${post.status === 'draft' ? `
                            <button class="btn btn-success btn-sm" onclick="changePostStatus(${post.id}, 'approved')">
                                <i class="fas fa-check icon"></i>Approve
                            </button>
                        ` : ''}
                        ${post.status === 'approved' ? `
                            <button class="btn btn-primary btn-sm" onclick="changePostStatus(${post.id}, 'posted')">
                                <i class="fas fa-paper-plane icon"></i>Mark as Posted
                            </button>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showAlert('Error loading posts: ' + error.message, 'danger');
    }
}

/**
 * Change post status
 * @param {number} postId - Post ID
 * @param {string} status - New status
 */
async function changePostStatus(postId, status) {
    try {
        const response = await fetch(`/api/posts/${postId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(`Post status updated to ${status}!`);
            loadPosts();
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error updating status: ' + error.message, 'danger');
    }
}

/**
 * Delete a post
 * @param {number} postId - Post ID to delete
 */
async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) return;

    try {
        const response = await fetch(`/api/posts/${postId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert('Post deleted successfully!');
            loadPosts();
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error deleting post: ' + error.message, 'danger');
    }
}

// ==================== Event Listeners ====================

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Event form submission
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const eventData = {
                title: document.getElementById('eventTitle').value,
                date: document.getElementById('eventDate').value,
                location: document.getElementById('eventLocation').value,
                type: document.getElementById('eventType').value,
                description: document.getElementById('eventDescription').value
            };

            try {
                const response = await fetch('/api/events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(eventData)
                });

                const data = await response.json();
                
                if (data.success) {
                    showAlert('Event created successfully!');
                    eventForm.reset();
                    loadEvents();
                } else {
                    showAlert('Error: ' + data.error, 'danger');
                }
            } catch (error) {
                showAlert('Error creating event: ' + error.message, 'danger');
            }
        });
    }

    // Generate post form submission
    const generateForm = document.getElementById('generateForm');
    if (generateForm) {
        generateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await generatePost();
        });
    }
}

// ==================== Initialization ====================

/**
 * Initialize the application
 */
function initialize() {
    loadTheme();
    initializeEventListeners();
    loadEvents();
}

// Run initialization when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

