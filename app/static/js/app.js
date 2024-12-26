// Global variables
let isDetectionActive = false;
const detectionsList = document.getElementById('detections-list');

// Start/Stop detection
function toggleDetection() {
    const toggleBtn = document.getElementById('toggle-detection');
    isDetectionActive = !isDetectionActive;
    
    toggleBtn.textContent = isDetectionActive ? 'Stop Detection' : 'Start Detection';
    toggleBtn.classList.toggle('active');
    
    if (isDetectionActive) {
        startDetection();
    }
}

// Fetch and display detections
async function updateDetections() {
    try {
        const response = await fetch('/api/detections');
        const detections = await response.json();
        
        displayDetections(detections);
    } catch (error) {
        console.error('Error fetching detections:', error);
    }
}

// Display detections in the list
function displayDetections(detections) {
    detectionsList.innerHTML = '';
    
    detections.forEach(detection => {
        const detectionElement = createDetectionElement(detection);
        detectionsList.appendChild(detectionElement);
    });
}

// Create detection list item
function createDetectionElement(detection) {
    const div = document.createElement('div');
    div.className = 'detection-item';
    
    div.innerHTML = `
        <div class="detection-info">
            <strong>Plate: ${detection.plate_number}</strong>
            <span>Time: ${new Date(detection.timestamp).toLocaleString()}</span>
        </div>
        <div class="detection-actions">
            <button class="btn btn-primary" onclick="printTicket('${detection.ticket_id}')">
                Print Ticket
            </button>
        </div>
    `;
    
    return div;
}

// Print ticket
async function printTicket(ticketId) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}/print`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.message) {
            showNotification('Ticket printed successfully', 'success');
        }
    } catch (error) {
        console.error('Error printing ticket:', error);
        showNotification('Error printing ticket', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Update detections periodically
setInterval(updateDetections, 5000);

// Initial update
updateDetections();