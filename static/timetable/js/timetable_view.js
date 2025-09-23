document.addEventListener('DOMContentLoaded', function() {
    // Initialize timetable
    initializeTimetable();
    
    // Filter functionality
    const filterInput = document.getElementById('timetable-filter');
    if (filterInput) {
        filterInput.addEventListener('input', function() {
            filterTimetable(this.value.toLowerCase());
        });
    }
    
    // Export buttons
    const exportPdfBtn = document.getElementById('export-pdf');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportTimetablePDF);
    }
    
    const exportImageBtn = document.getElementById('export-image');
    if (exportImageBtn) {
        exportImageBtn.addEventListener('click', exportTimetableImage);
    }
    
    // Print functionality
    const printBtn = document.getElementById('print-timetable');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
});

function initializeTimetable() {
    // Add click handlers to class cells for editing
    const classCells = document.querySelectorAll('.class-cell');
    classCells.forEach(cell => {
        cell.addEventListener('click', function() {
            const classId = this.getAttribute('data-class-id');
            if (classId) {
                window.location.href = `/class/${classId}/edit/`;
            }
        });
    });
    
    // Initialize tooltips if using a library like Bootstrap
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }
}

function filterTimetable(filterText) {
    const classCells = document.querySelectorAll('.class-cell');
    
    if (!filterText) {
        // Show all cells if no filter text
        classCells.forEach(cell => {
            cell.style.display = '';
        });
        
        // Also show all rows
        const rows = document.querySelectorAll('.timetable-grid tr');
        rows.forEach(row => {
            row.style.display = '';
        });
        
        return;
    }
    
    // Filter cells based on content
    classCells.forEach(cell => {
        const subject = cell.getAttribute('data-subject') || '';
        const instructor = cell.getAttribute('data-instructor') || '';
        const location = cell.getAttribute('data-location') || '';
        
        const matches = subject.toLowerCase().includes(filterText) || 
                       instructor.toLowerCase().includes(filterText) || 
                       location.toLowerCase().includes(filterText);
        
        if (matches) {
            cell.style.display = '';
        } else {
            cell.style.display = 'none';
        }
    });
    
    // Also hide empty rows
    const rows = document.querySelectorAll('.timetable-grid tr');
    rows.forEach((row, index) => {
        if (index === 0) return; // Skip header row
        
        let hasVisibleCell = false;
        const cells = row.querySelectorAll('td');
        
        cells.forEach((cell, cellIndex) => {
            if (cellIndex === 0) return; // Skip time column
            
            if (cell.classList.contains('class-cell') && cell.style.display !== 'none') {
                hasVisibleCell = true;
            }
        });
        
        // Hide entire row if no visible cells
        if (!hasVisibleCell) {
            row.style.display = 'none';
        } else {
            row.style.display = '';
        }
    });
}

// Export functionality using ReportLab (as shown in search results)
function exportTimetablePDF() {
    // Create a form and submit it to trigger PDF generation
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = window.location.href;
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'export_pdf';
    input.value = '1';
    form.appendChild(input);
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

function exportTimetableImage() {
    // Check if html2canvas is available
    if (typeof html2canvas === 'undefined') {
        alert('Image export requires the html2canvas library. Please add it to your project.');
        return;
    }
    
    // Use html2canvas to capture the timetable as an image
    html2canvas(document.getElementById('timetable-container')).then(function(canvas) {
        // Convert canvas to image data URL
        const imageData = canvas.toDataURL('image/png');
        
        // Create a temporary link to download the image
        const link = document.createElement('a');
        link.download = 'timetable.png';
        link.href = imageData;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }).catch(function(error) {
        console.error('Error exporting image:', error);
        alert('Error exporting image. Please check the console for details.');
    });
}

// Utility function to convert time to grid position
function timeToPosition(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return (hours - 8) * 2 + (minutes / 30); // Assuming 8am start and 30min intervals
}

// Utility function to calculate duration in grid cells
function calculateDuration(startTime, endTime) {
    const start = timeToPosition(startTime);
    const end = timeToPosition(endTime);
    return end - start;
}

