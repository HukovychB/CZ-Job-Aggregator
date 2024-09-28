// JS SCRIPT FOR THE INDEX.HTML PAGE

document.addEventListener('DOMContentLoaded', function() {
    // ------------------------------------------------------------------------------------------
    // CHECKBOXES FUNCTIONALITY
    // ------------------------------------------------------------------------------------------
    const allSitesCheckbox = document.getElementById('all_sites');
    const siteCheckboxes = document.querySelectorAll('input[name="sites"]:not(#all_sites)');

    allSitesCheckbox.addEventListener('change', function() {
        for (const checkbox of siteCheckboxes) {
            checkbox.checked = this.checked;
        }
    });

    for (const checkbox of siteCheckboxes) {
        checkbox.addEventListener('change', function() {
            if (!this.checked) {
                allSitesCheckbox.checked = false;
            } else {
                const allChecked = Array.from(siteCheckboxes).every(cb => cb.checked);
                allSitesCheckbox.checked = allChecked;
            }
        });
    }

    // ------------------------------------------------------------------------------------------
    // ANIMATED TEXT
    // ------------------------------------------------------------------------------------------
    const textElement = document.getElementById('animated-text');
    const texts = ["Search", "Scrape", "Spider", "Seek", "Survey", "Sniff"];
    let textIndex = 0;
    // Start from the second letter
    let charIndex = 1;
    let isDeleting = false;

    function type() {
        const currentText = texts[textIndex];
        if (isDeleting) {
            textElement.textContent = currentText.charAt(0) + currentText.substring(1, charIndex--);
            // Keep the first letter
            if (charIndex < 1) {
                isDeleting = false;
                textIndex = (textIndex + 1) % texts.length;
                // Reset to start from the second letter
                charIndex = 1; 
            }
        } else {
            textElement.textContent = currentText.charAt(0) + currentText.substring(1, charIndex++);
            if (charIndex > currentText.length) {
                isDeleting = true;
            }
        }
        setTimeout(type, isDeleting ? 150 : 400);
    }

    type();
});