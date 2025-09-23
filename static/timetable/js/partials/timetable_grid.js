// Timetable grid rendering functions
class TimetableGrid {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            startHour: 8,
            endHour: 20,
            timeInterval: 30,
            days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            ...options
        };
        
        if (!this.container) {
            console.error(`Container with ID ${containerId} not found`);
            return;
        }
        
        this.classes = [];
        this.initialize();
    }
    
    initialize() {
        this.renderGrid();
    }
    
    renderGrid() {
        // Clear container
        this.container.innerHTML = '';
        
        // Create table
        const table = document.createElement('table');
        table.className = 'timetable-grid';
        
        // Create header row with days
        const headerRow = document.createElement('tr');
        headerRow.appendChild(document.createElement('th')); // Empty cell for time column
        
        this.options.days.forEach(day => {
            const th = document.createElement('th');
            th.textContent = day;
            headerRow.appendChild(th);
        });
        
        table.appendChild(headerRow);
        
        // Create time rows
        for (let hour = this.options.startHour; hour < this.options.endHour; hour++) {
            for (let min = 0; min < 60; min += this.options.timeInterval) {
                const row = document.createElement('tr');
                
                // Time cell
                const timeCell = document.createElement('td');
                timeCell.className = 'time-cell';
                timeCell.textContent = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
                row.appendChild(timeCell);
                
                // Empty cells for each day
                this.options.days.forEach(() => {
                    const cell = document.createElement('td');
                    cell.setAttribute('data-time', `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`);
                    row.appendChild(cell);
                });
                
                table.appendChild(row);
            }
        }
        
        this.container.appendChild(table);
    }
    
    addClass(classData) {
        this.classes.push(classData);
        this.renderClasses();
    }
    
    renderClasses() {
        // Clear existing classes
        const classCells = this.container.querySelectorAll('.class-cell');
        classCells.forEach(cell => cell.remove());
        
        // Add classes to grid
        this.classes.forEach(classData => {
            const { day, startTime, endTime, subject, location, instructor, color, id } = classData;
            
            // Calculate position and duration
            const startPos = this.timeToPosition(startTime);
            const duration = this.calculateDuration(startTime, endTime);
            
            // Find the correct cell
            const dayIndex = this.options.days.indexOf(day) + 1; // +1 for time column
            const cell = this.container.querySelector(`tr:nth-child(${startPos + 1}) td:nth-child(${dayIndex + 1})`);
            
            if (cell) {
                // Create class element
                const classElement = document.createElement('div');
                classElement.className = 'class-cell';
                classElement.classList.add('class-info');
                classElement.style.backgroundColor = color || '#e0e0e0';
                classElement.setAttribute('data-class-id', id);
                classElement.setAttribute('data-subject', subject);
                classElement.setAttribute('data-instructor', instructor);
                classElement.setAttribute('data-location', location);
                
                // Set rowspan based on duration
                cell.rowSpan = duration;
                cell.appendChild(classElement);
                
                // Add class content
                classElement.innerHTML = `
                    <div class="class-subject">${subject}</div>
                    <div class="class-details">${location} | ${instructor}</div>
                `;
                
                // Add click event
                classElement.addEventListener('click', () => {
                    if (this.options.onClassClick) {
                        this.options.onClassClick(classData);
                    }
                });
            }
        });
    }
    
    timeToPosition(time) {
        const [hours, minutes] = time.split(':').map(Number);
        return (hours - this.options.startHour) * (60 / this.options.timeInterval) + (minutes / this.options.timeInterval);
    }
    
    calculateDuration(startTime, endTime) {
        const start = this.timeToPosition(startTime);
        const end = this.timeToPosition(endTime);
        return end - start;
    }
    
    clear() {
        this.classes = [];
        this.renderClasses();
    }
}

// Initialize timetable grid when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.timetableGrid = new TimetableGrid('timetable-container', {
        onClassClick: function(classData) {
            window.location.href = `/class/${classData.id}/edit/`;
        }
    });
    
    // Load classes from data attribute if available
    const container = document.getElementById('timetable-container');
    if (container && container.dataset.classes) {
        try {
            const classes = JSON.parse(container.dataset.classes);
            classes.forEach(classData => {
                window.timetableGrid.addClass(classData);
            });
        } catch (e) {
            console.error('Error parsing classes data:', e);
        }
    }
});


