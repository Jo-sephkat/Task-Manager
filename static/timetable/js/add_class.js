document.addEventListener('DOMContentLoaded', function() {
    // Time validation
    const startTimeInput = document.querySelector('input[name="start_time"]');
    const endTimeInput = document.querySelector('input[name="end_time"]');
    
    if (startTimeInput && endTimeInput) {
        startTimeInput.addEventListener('change', validateTimes);
        endTimeInput.addEventListener('change', validateTimes);
    }
    
    // Form validation
    const classForm = document.getElementById('class-form');
    if (classForm) {
        classForm.addEventListener('submit', function(e) {
            if (!validateTimes()) {
                e.preventDefault();
            }
        });
    }
});

function validateTimes() {
    const startTimeInput = document.querySelector('input[name="start_time"]');
    const endTimeInput = document.querySelector('input[name="end_time"]');
    const errorDiv = document.getElementById('time-error');
    
    if (!startTimeInput.value || !endTimeInput.value) {
        return true; // Let required field validation handle empty fields
    }
    
    const startTime = new Date(`2000-01-01T${startTimeInput.value}`);
    const endTime = new Date(`2000-01-01T${endTimeInput.value}`);
    
    if (startTime >= endTime) {
        // Show error message
        if (!errorDiv) {
            const newErrorDiv = document.createElement('div');
            newErrorDiv.id = 'time-error';
            newErrorDiv.className = 'error-message';
            newErrorDiv.textContent = 'End time must be after start time.';
            endTimeInput.parentNode.appendChild(newErrorDiv);
        } else {
            errorDiv.textContent = 'End time must be after start time.';
        }
        
        // Highlight problematic fields
        startTimeInput.style.borderColor = 'red';
        endTimeInput.style.borderColor = 'red';
        
        return false;
    } else {
        // Remove error message if it exists
        if (errorDiv) {
            errorDiv.remove();
        }
        
        // Reset border color
        startTimeInput.style.borderColor = '';
        endTimeInput.style.borderColor = '';
        
        return true;
    }
}

