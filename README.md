# DairyCrawler
## A mini crawler to crawl my personal dairy

Crawl data frome icity, and save corresponding dairy text and pictures, meta info.
  
## Logic
1. Get response from welcome page.
2. Fetch authen token, fillin username and password to form signin.json.
3. Post signin request, get response, go to callback function.
4. Pass source code to beautifulsoup, which can parse infomation more efficiently.
5. Get all info we need for each dairy.
6. Save all info to each individual file, including the original images.
7. Get next page url, go to next page
8. End

## Usage (Assume you know a shit to CS)
1. This crawler built on top of [scrapy](https://scrapy.org/), and it's written on Linux, needs further efforts to make it compatible to Windows system (which apparently I won't do)
2. Sample command:
    `scrapy runspider {path_to_crawler.py}`
3. Remeber to fill in your username and pwd.