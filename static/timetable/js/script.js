document.addEventListener('DOMContentLoaded', function() {
    // Color picker functionality
    const colorInput = document.getElementById('id_color');
    const colorPreview = document.getElementById('color-preview');
    
    if (colorInput && colorPreview) {
        // Update preview when color changes
        colorInput.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });
        
        // Set initial preview color
        colorPreview.style.backgroundColor = colorInput.value || '#ffffff';
    }
    
    // Random color generator
    const randomColorBtn = document.getElementById('random-color-btn');
    if (randomColorBtn && colorInput) {
        randomColorBtn.addEventListener('click', function() {
            const randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
            colorInput.value = randomColor;
            if (colorPreview) {
                colorPreview.style.backgroundColor = randomColor;
            }
        });
    }
    
    // Form validation
    const subjectForm = document.getElementById('subject-form');
    if (subjectForm) {
        subjectForm.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('id_name');
            if (nameInput && !nameInput.value.trim()) {
                e.preventDefault();
                alert('Subject name is required');
                nameInput.focus();
            }
        });
    }
    
    // Auto-generate code from name
    const nameInput = document.getElementById('id_name');
    const codeInput = document.getElementById('id_code');
    
    if (nameInput && codeInput && !codeInput.value) {
        nameInput.addEventListener('blur', function() {
            if (!codeInput.value && this.value) {
                // Generate code from name (first 3 letters uppercase)
                const code = this.value.replace(/\s+/g, '').substring(0, 3).toUpperCase();
                codeInput.value = code;
            }
        });
    }
});


