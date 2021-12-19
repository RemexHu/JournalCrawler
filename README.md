# DairyCrawler
## A mini crawler to crawl my personal dairy

> Crawl data frome icity, and save corresponding dairy text and pictures, meta info.
  
## Logic
1. Get response from welcome page.
2. Fetch authen token, fillin username and password to form signin.json.
3. Post signin request, get response, go to callback function.
4. Pass source code to beautifulsoup, which can parse infomation more efficiently.
5. Get all info we need for each dairy.
6. Save all info to each individual file.
7. Get next page url, go to next page
8. End
