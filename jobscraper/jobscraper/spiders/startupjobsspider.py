# STARTUPJOBS.CZ SPIDER

import scrapy
from jobscraper.jobscraper.items import JobsItem

class StartupSpider(scrapy.Spider):
    def __init__(self, job=None, location=None, run_id=None, *args, **kwargs):
        super(StartupSpider, self).__init__(*args, **kwargs)
        self.job = job.strip().replace(" ", "+")
        # No location parameter for startupjobs.cz
        self.start_urls = [f"https://www.startupjobs.cz/api/offers?page=1&superinput%5B%5D={self.job}&disable-reorder=1"]
        self.run_id = run_id

    name = "startup"
    allowed_domains = ["startupjobs.cz", "proxy.scrapeops.io"]

    def parse(self, response):
        # Get all jobs cards
        jobs = response.json().get('resultSet', [])

        # Loop through each job card and extract the data
        for job in jobs:
            job_item = JobsItem()

            job_item["title"] = job.get("name")
            # Format: '/nabidka/80937/technical-analyst'
            job_item["link"] = job.get("url")
            job_item["company"] = job.get("company")
            job_item["location"] = job.get("locations")
            salary = job.get("salary")
            if salary:
                job_item["salary"] = f"{salary['min']}-{salary['max']} {salary['currency']}/{salary['measure']}"
            else:
                job_item["salary"] = ""
            job_item["published"] = ""
            job_item["source"] = "startupjobs.cz"
            job_item["run_id"] = self.run_id

            yield job_item
        
        # Go to the next page and repeat
        current_page = response.url.split("page=")[-1].split("&")[0]
        next_page = int(current_page) + 1
        next_page_url = f"https://www.startupjobs.cz/api/offers?page={next_page}&superinput%5B%5D=Analyst&disable-reorder=1"

        # If there are jobs in the current response, continue to the next page
        if jobs:
            yield scrapy.Request(url=next_page_url, callback=self.parse)