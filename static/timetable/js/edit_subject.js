document.addEventListener('DOMContentLoaded', function() {
    // Color picker functionality
    const colorInput = document.getElementById('id_color');
    const colorPreview = document.getElementById('color-preview');
    
    // Initialize color preview
    function initializeColorPreview() {
        if (colorInput && colorPreview) {
            // Set initial preview color
            const initialColor = colorInput.value || '#ffffff';
            colorPreview.style.backgroundColor = initialColor;
            
            // Update preview when color changes
            colorInput.addEventListener('input', function() {
                colorPreview.style.backgroundColor = this.value;
            });
        }
    }
    
    // Random color generator
    function setupRandomColorButton() {
        const randomColorBtn = document.getElementById('random-color-btn');
        if (randomColorBtn && colorInput) {
            randomColorBtn.addEventListener('click', function() {
                const randomColor = generateRandomColor();
                colorInput.value = randomColor;
                if (colorPreview) {
                    colorPreview.style.backgroundColor = randomColor;
                }
            });
        }
    }
    
    // Generate a random hex color
    function generateRandomColor() {
        return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
    }
    
    // Form validation
    function setupFormValidation() {
        const subjectForm = document.getElementById('subject-form');
        if (subjectForm) {
            subjectForm.addEventListener('submit', function(e) {
                const nameInput = document.getElementById('id_name');
                if (nameInput && !nameInput.value.trim()) {
                    e.preventDefault();
                    showError('Subject name is required', nameInput);
                    nameInput.focus();
                    return false;
                }
                
                // Validate color format
                if (colorInput && colorInput.value) {
                    const colorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
                    if (!colorRegex.test(colorInput.value)) {
                        e.preventDefault();
                        showError('Please enter a valid hex color code (e.g., #FF5733)', colorInput);
                        colorInput.focus();
                        return false;
                    }
                }
                
                return true;
            });
        }
    }
    
    // Show error message
    function showError(message, inputElement) {
        // Remove existing error messages
        const existingErrors = document.querySelectorAll('.inline-error');
        existingErrors.forEach(error => error.remove());
        
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'inline-error error-message';
        errorDiv.textContent = message;
        errorDiv.style.color = '#dc3545';
        errorDiv.style.marginTop = '5px';
        errorDiv.style.fontSize = '14px';
        
        // Insert after input element
        inputElement.parentNode.insertBefore(errorDiv, inputElement.nextSibling);
        
        // Highlight input
        inputElement.style.borderColor = '#dc3545';
        
        // Remove highlight after 3 seconds
        setTimeout(() => {
            inputElement.style.borderColor = '';
        }, 3000);
    }
    
    // Auto-generate code from name
    function setupAutoCodeGeneration() {
        const nameInput = document.getElementById('id_name');
        const codeInput = document.getElementById('id_code');
        
        if (nameInput && codeInput) {
            nameInput.addEventListener('blur', function() {
                // Only auto-generate if code field is empty
                if (!codeInput.value.trim() && this.value.trim()) {
                    const code = generateSubjectCode(this.value);
                    codeInput.value = code;
                }
            });
        }
    }
    
    // Generate subject code from name
    function generateSubjectCode(name) {
        // Remove special characters and extra spaces
        const cleanName = name.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, ' ').trim();
        
        // Get first 3-4 characters
        if (cleanName.length <= 3) {
            return cleanName.toUpperCase();
        }
        
        // For longer names, try to create acronym
        const words = cleanName.split(' ');
        if (words.length > 1) {
            // Use first letters of first 3 words
            return words.slice(0, 3).map(word => word.charAt(0).toUpperCase()).join('');
        } else {
            // Use first 3-4 characters of single word
            return cleanName.substring(0, 4).toUpperCase();
        }
    }
    
    // Enhanced input styling
    function enhanceInputStyles() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="color"]');
        inputs.forEach(input => {
            // Add focus styles
            input.addEventListener('focus', function() {
                this.style.borderColor = '#4a6fa5';
                this.style.boxShadow = '0 0 5px rgba(74, 111, 165, 0.3)';
            });
            
            input.addEventListener('blur', function() {
                this.style.borderColor = '#ddd';
                this.style.boxShadow = 'none';
            });
        });
    }
    
    // Setup color input with better UX
    function setupColorInput() {
        if (colorInput) {
            // Add a custom color picker trigger
            colorInput.style.display = 'none'; // Hide the default color input
            
            const customColorPicker = document.createElement('div');
            customColorPicker.style.display = 'flex';
            customColorPicker.style.alignItems = 'center';
            customColorPicker.style.gap = '10px';
            customColorPicker.style.marginTop = '5px';
            
            const colorDisplay = document.createElement('div');
            colorDisplay.style.width = '40px';
            colorDisplay.style.height = '40px';
            colorDisplay.style.borderRadius = '4px';
            colorDisplay.style.border = '1px solid #ddd';
            colorDisplay.style.cursor = 'pointer';
            colorDisplay.style.backgroundColor = colorInput.value || '#ffffff';
            
            const colorValue = document.createElement('span');
            colorValue.textContent = colorInput.value || '#FFFFFF';
            colorValue.style.fontFamily = 'monospace';
            colorValue.style.fontSize = '14px';
            
            colorDisplay.addEventListener('click', function() {
                colorInput.click();
            });
            
            colorInput.addEventListener('input', function() {
                colorDisplay.style.backgroundColor = this.value;
                colorValue.textContent = this.value;
                if (colorPreview) {
                    colorPreview.style.backgroundColor = this.value;
                }
            });
            
            customColorPicker.appendChild(colorDisplay);
            customColorPicker.appendChild(colorValue);
            
            colorInput.parentNode.insertBefore(customColorPicker, colorInput.nextSibling);
        }
    }
    
    // Initialize all functionality
    function initializeAll() {
        initializeColorPreview();
        setupRandomColorButton();
        setupFormValidation();
        setupAutoCodeGeneration();
        enhanceInputStyles();
        setupColorInput();
        
        console.log('Subject form initialized successfully');
    }
    
    // Run initialization
    initializeAll();
});

