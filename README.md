# CZ-Job-Aggregator

#### Video Demo:  https://youtu.be/heSWT1qmxPo
#### Website Page:

## Overview

This is a website aggregator of job vacancies mainly focused on the Czech Republic. It is built using the *Flask* framework, which allows users to have secure personal accounts and navigate through various pages of the website. Initially, it offers users the option to log in or register for the website. After the authentication procedure, the main page is displayed, allowing users to search for jobs of their interest in their preferred location. Additionally, users can select from which websites they want to see vacancies.

**The jobs are scraped from 5 different websites:**
- **[LinkedIn.com](https://www.linkedin.com)**
- **[Indeed.com](https://www.indeed.com)** 
- **[Startupjobs.cz](https://www.startupjobs.cz)**
- **[Jobs.cz](https://www.jobs.cz)**
- **[Prace.cz](https://www.prace.cz)**

After the search procedure begins, the jobs are dynamically added to the pages as they are scraped. Each job card contains information about the job title, company name, location, the date it was published, and salary if available. Additionally, users can sort the job listings based on their published date to see the most recent listings.

Users can add any job to their list of favorites. These can be found on the *My Jobs* page. There, for each job, different statuses can be set such as *Interesting, Applied, Interview Scheduled, Offer Received, and Denied/No Answer*. These favorite jobs, along with their statuses set by users, are stored in the database, so they are preserved even if a user logs out and subsequently comes back. Additionally, on the *My Jobs* page, users can filter jobs based on their statuses.

## Decralation 

*The author does not intend to use the scraped data for commercial purposes or any similar activities. The goals of this project are purely educational.*

## Features

- **User Authentication**: Secure login and registration for users based on username and password. Passwords are stored in the database as hashes.

- **Job Search**: Search for jobs based on keywords and location. The search is the most effective for Czech cities, *however it could be used for any city if only LinkedIn option for seach is selected*

- **Website Selection**: Choose specific websites among 5 listed to scrape job listings from.

- **Dynamic Job Listings**: Similar jobs are first fetched from the database that is populated by previous users' searches and then jobs are dynamically added to the page as they are scraped.

- **Job Information**: Each job card displays the job title, company name, location, publication date, and salary (if available).

- **Sorting**: Sort job listings by their publication date to see the most recent listings.

- **Favorites Management**: Add jobs to a list of favorites. Also, removing from the list is available

- **Status Tracking**: Set and track statuses for favorite jobs (e.g., Interesting, Applied, Interview Scheduled, Offer Received, Denied/No Answer).

- **Persistent Storage**: Favorite jobs and their statuses are stored in the database and preserved across sessions.

- **Filtering**: Filter favorite jobs based on their statuses.

## Code Design

### Run.py

- This file runs the app

### Flask

- The Flask framework is utilized to develop the dynamic website, enabling **POST** requests. 
- All related files are stored in `app/` folder
- HTML pages are stored in `app/templates/` folder
- CSS file, Java Script files, and media files are stored in `app/static/` folder 
- Routes are defined in `app/routes.py`. 
- `app/__init__.py` initializes Flask app
- Most routes are protected with the *@login_required* decorator to ensure that only authenticated users can access the website.

### Scrapy

- The Scrapy framework is used for large-scale web scraping.
- All spiders and related components are located in the `jobscraper/` folder.
- Each website has a dedicated spider in folder `jobscraper/jobscraper/spiders/`.
- Spiders request the first page of job listings, extract available listings, and proceed to the next page if available.
- The `JobsItem` Scrapy item is common to all spiders and defined in `jobscraper/jobscraper/items.py`.
- Two pipelines are applied to each scraped item defined in `jobscraper/jobscraper/pipelines.py`:
    - `JobscraperPipeline`: Cleans the data.
    - `SaveToMySQLPipeline`: Saves the item to the `jobs_active` database table.
- Two middlewares from [ScrapeOps](https://scrapeops.io/) are used to avoid detection by anti-bot systems defined in `jobscraper/jobscraper/middlewares.py`:
    - `ScrapeOpsFakeBrowserHeaderAgentMiddleware`: Sends random headers in requests.
    - `ScrapeOpsScrapyProxySdk`: Uses a proxy network to change IP addresses.
- Scrapy settigns are in `jobscraper/jobscraper/settings.py`

### Database

- *MySQL* database is used in this case
- Tables are defined in `app/__init__.py`
- `users_logs`: stores users credentials. Passwords are stored as hashes
- `jobs_active`: stores jobs listings after they are scraped 
- `jobs_inactive`: stores jobs listings that are more than 30 days old
- `favorite_jobs`: stores favorite jobs listings for each user

## Licence
This project is licensed and prohibits any distribution or commercial use. See the [LICENCE](LICENCE.htm) file for details.


