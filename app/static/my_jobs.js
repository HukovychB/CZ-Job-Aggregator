// JS SCRIPT FOR THE MY_JOBS.HTML PAGE

document.addEventListener('DOMContentLoaded', function() {
    // ------------------------------------------------------------------------------------------
    // REMOVE BTN FUNCTIONALITY
    // ------------------------------------------------------------------------------------------
    const favoriteButtons = document.querySelectorAll('.remove-btn');

    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            event.preventDefault(); 

            const jobCard = button.closest('.card');
            const jobCardFull = button.closest('.col-12.mb-4');
            const jobData = {
                title: jobCard.querySelector('.card-title').textContent.trim(),
                published: jobCard.querySelector('.text-muted').textContent.trim(),
                company: jobCard.querySelector('.card-subtitle').textContent.trim(),
                location: jobCard.querySelector('.card-text').textContent.trim(),
                salary: jobCard.querySelector('.salary-container .card-text') ? jobCard.querySelector('.salary-container .card-text').textContent.trim() : null,
                link: jobCard.closest('a').href
            };

            fetch('/remove_from_favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jobData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    jobCardFull.remove();
                } else {
                    alert('Failed to remove from favorites.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to remove from favorites.');
            });
        });
    });

    // ------------------------------------------------------------------------------------------
    // IF NO JOBS, DISPLAY NO JOBS MESSAGE
    // ------------------------------------------------------------------------------------------
    const jobContainer = document.querySelector('.row.mt-5');
    if (jobContainer.children.length === 0) {
            document.getElementById('no-jobs').style.display = 'block';
    }

    // ------------------------------------------------------------------------------------------
    // STATUS DROPDOWN FUNCTIONALITY
    // ------------------------------------------------------------------------------------------
    const statusDropdowns = document.querySelectorAll('.status-dropdown');

    statusDropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(event) {
            event.stopPropagation();
            event.preventDefault();
        })
    })

    statusDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function(event) {
            const selectedStatus = event.target.value;
            const jobCard = dropdown.closest('.card');
            const jobData = {
                title: jobCard.querySelector('.card-title').textContent.trim(),
                published: jobCard.querySelector('.text-muted').textContent.trim(),
                company: jobCard.querySelector('.card-subtitle').textContent.trim(),
                location: jobCard.querySelector('.card-text').textContent.trim(),
                salary: jobCard.querySelector('.salary-container .card-text') ? jobCard.querySelector('.salary-container .card-text').textContent.trim() : null,
                link: jobCard.closest('a').href,
                status: selectedStatus
            };

            fetch('/update_job_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jobData)
            })
            .then(response => response.json())
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update job status.');
            });
        });
    });

    // Function to update the background color of the select element
    statusDropdowns.forEach(dropdown => {
        function updateBackgroundColor() {
            const selectedOption = dropdown.options[dropdown.selectedIndex];
            dropdown.style.backgroundColor = selectedOption.style.backgroundColor;
            dropdown.style.color = selectedOption.style.color;
        }

        updateBackgroundColor();

        dropdown.addEventListener('change', updateBackgroundColor);
    });


    // Function to filter job cards based on the selected status
    const filterDropdown = document.getElementById('filter-status');
    const jobCards = document.querySelectorAll('.col-12.mb-4');

    function filterJobCards() {
        const selectedStatus = filterDropdown.value;
        jobCards.forEach(card => {
            const cardStatus = card.querySelector('.status-dropdown').value;
            if (selectedStatus === 'all' || cardStatus === selectedStatus) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });

        // Show or hide the "no jobs" message
        const visibleCards = Array.from(jobCards).filter(card => card.style.display === 'block');
        document.getElementById('no-jobs').style.display = visibleCards.length ? 'none' : 'block';
    }

    filterJobCards();

    filterDropdown.addEventListener('change', filterJobCards);
});