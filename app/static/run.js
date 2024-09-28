// JS SCRIPT FOR THE RUN.HTML PAGE

const REFRESH_TIME = 2000;
const TIME_TO_DISPLAY_NO_JOBS = 30000;

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
    // QUERY DATABASE FOR JOBS AND DISPLAY THEM IN INTERVALS 
    // ------------------------------------------------------------------------------------------
    function fetchJobs() {
        fetch('/api/jobs')
            .then(response => response.json())
            .then(data => {
                const jobContainer = document.querySelector('.row.mt-5');

                data.jobs.forEach(job => {
                    let salaryHtml = '';
                    if (job.salary) {
                        salaryHtml = `
                            <div class="salary-container">
                                <p class="card-text"><b><i>${job.salary}</i></b></p>
                            </div>
                        `;
                    }

                    const jobCard = `
                        <div class="col-12 mb-4">
                            <a href="${job.link}" class="card text-decoration-none custom-card align-center">
                                <div class="card-body d-flex flex-column">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div class="d-flex align-items-center">
                                            <h5 class="card-title"><b>${job.title}</b></h5>
                                            <button class="favorite-btn"><i>Add to favorites</i></button>
                                        </div>
                                        <p class="text-muted">${job.published}</p>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <img src="../static/company.svg" alt="Company Icon" class="company-icon">
                                        <h6 class="card-subtitle mb-2 text-muted">${job.company}</h6>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <img src="../static/place.svg" alt="Location Icon" class="location-icon">
                                        <p class="card-text">${job.location}</p>
                                    </div>
                                    ${salaryHtml}
                                </div>
                            </a>
                            <hr>
                        </div>
                    `;
                    jobContainer.insertAdjacentHTML('beforeend', jobCard);
                });

            // Hide loader if spiders have been stopped
            if (data.spiders_stopped) {
                document.getElementById('loader').style.display = 'none';
            }
            })
            .catch(error => console.error('Error fetching jobs:', error));
    }

    setInterval(fetchJobs, REFRESH_TIME);

    // ------------------------------------------------------------------------------------------
    // IF NO JOBS ARE LOADED AFTER A CERTAIN TIME, DISPLAY NO JOBS MESSAGE
    // ------------------------------------------------------------------------------------------
    function checkJobContainer() {
        const jobContainer = document.querySelector('.row.mt-5');
        if (jobContainer.children.length === 0) {
            document.getElementById('loader').style.display = 'none';
            document.getElementById('no-jobs').style.display = 'block';
        }
    }

    setInterval(checkJobContainer, TIME_TO_DISPLAY_NO_JOBS);

    // ------------------------------------------------------------------------------------------
    // SORT BUTTON FUNCTIONALITY
    // ------------------------------------------------------------------------------------------

    document.querySelector('#sort-date-btn').onclick = function() {
        const jobContainer = document.querySelector('.row.mt-5');
        const jobCards = Array.from(jobContainer.children);
        console.log(jobCards[1]);

        jobCards.sort((a, b) => {
            const dateA = new Date(a.querySelector('.d-flex.justify-content-between.align-items-start .text-muted').textContent);
            const dateB = new Date(b.querySelector('.d-flex.justify-content-between.align-items-start .text-muted').textContent);
            return dateB - dateA;
        });

        jobContainer.innerHTML = '';
        jobCards.forEach(card => jobContainer.appendChild(card));   
    }

    // SORT BUTTON DISPLAY IF JOBS ARE LOADED RIGHT AWAY
    if (document.querySelector('.row.mt-5').children.length !== 0) {
        document.getElementById('sort-date-btn').style.display = 'block';
    }

    // DISPLAY SORT BUTTON WHEN JOBS ARE LOADED AFTER A CERTAIN TIME
    const targetNode = document.querySelector('.row.mt-5');

    const config = { childList: true };

    const callback = function(mutationsList, observer) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList' && targetNode.children.length > 0) {
                document.getElementById('sort-date-btn').style.display = 'block';
                observer.disconnect();
                break;
            }
        }
    };


    const observer = new MutationObserver(callback);

    observer.observe(targetNode, config);

    // ------------------------------------------------------------------------------------------
    // ADD TO FAVORITES FUNCTIONALITY
    // ------------------------------------------------------------------------------------------
    document.querySelector('.row.mt-5').addEventListener('click', function(event) {
        if (event.target.closest('.favorite-btn')) {
            event.stopPropagation();
            event.preventDefault();
    
            const favoriteButton = event.target.closest('.favorite-btn');
            const jobCard = favoriteButton.closest('.card');
            const jobData = {
                title: jobCard.querySelector('.card-title').textContent.trim(),
                published: jobCard.querySelector('.text-muted').textContent.trim(),
                company: jobCard.querySelector('.card-subtitle').textContent.trim(),
                location: jobCard.querySelector('.card-text').textContent.trim(),
                salary: jobCard.querySelector('.salary-container .card-text') ? jobCard.querySelector('.salary-container .card-text').textContent.trim() : null,
                link: jobCard.closest('a').href
            };
    
            fetch('/add_to_favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jobData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    favoriteButton.innerHTML = '✔ Added to favorites!';
                    favoriteButton.classList.add('added-to-favorites');
                } else {
                    alert('Failed to add to favorites. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to add to favorites. Please try again.');
            });
        }
    });
});
