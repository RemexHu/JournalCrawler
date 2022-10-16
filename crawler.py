from bs4 import BeautifulSoup
import scrapy
import os
import dateutil.parser
import time
import requests

class JournalSpider(scrapy.Spider):
    name = 'icityJournalBackup'
    start_urls = ['https://icity.ly/welcome']
    # font color options: https://www.w3schools.com/tags/ref_colornames.asp

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.url_prefix = 'https://icity.ly/'
        self.save_prefix = 'the_directory_path_you_want_to_save' # <============= Fill in by yourself
        self.default_time_color = 'linen'
        self.default_location_color = 'mintcream'
        self.month_dict = {1: 'Jan', 2: 'Feb', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'Aug', 9: 'Sept',
                            10: 'Oct', 11: 'Nov', 12: 'Dec'}
    
    def get_font_color(self, color, text):
        return f"""<span style="color:{color}">{text}</span>"""

    def parse(self, response):
        print(f"===> request before login url: {response.url}")
        username = 'your_username'       # <============= Fill in by yourself
        password = 'your_password'       # <============= Fill in by yourself
        authenticity_token = response.css("head meta::attr(content)")[3].get()
        utf8 = '✓'
        commit = '登入'

        login_data = {'utf8': utf8, 'authenticity_token': authenticity_token,
            'icty_user[login]': username, 'icty_user[password]': password,
            'icty_user[remember_me]': '1', 'commit': commit}
        print(login_data)
        return scrapy.FormRequest.from_response(
            response,
            formdata=login_data,
            callback=self.parse_after_login
        )
    
    def parse_after_login(self, response):
        print(f"===> request after login url: {response.url}")
        print(f"===> Start to crawl dairies in this page")
        soup = BeautifulSoup(response.text, 'html.parser')
        dairies = soup.body.find('div', {"class": "container below-top-navbar"}).find('div', {"class": "mw-box gma600 tp"}).find('div', {"class": "cntr"}).ul.find_all('li', {"data-expand": "true"})
        for i, journal in enumerate(dairies):
            self.parse_journal(i, journal)
        next_page_suffix = soup.find("a", {"data-role": "load-more-trigger"})['href']
        next_page_url = self.url_prefix + next_page_suffix
        print(f"===> Finish crawling dairies in this page")
        time.sleep(0.1)
        print(f"===> Request next page: {next_page_url}")
        request = scrapy.Request(url=next_page_url, callback=self.parse_after_login)
        yield request


    def parse_journal(self, i, journal):
        print(f"===> start to parse no.{i} journal...")
        journal_text = str(journal.find('div', {"class": "comment"}))[21:-6].replace("<br/>", "\n")
        print(f"text before strip: {journal_text}")
        if "ttt=" in journal_text:
            journal_text = journal_text.split('#')[1].split('<')[0]
        journal_title = journal.find('h4').text if journal.find('h4') else journal_text.split(',')[0][:20].replace(' ', '').replace('/', '')

        journal_weather_location = journal.find('span', {"class": "location"})
        journal_real_weather = journal_weather_location.i['class'][1][15:] if journal_weather_location else 'Unkown weather'

        journal_real_location = journal_weather_location.text if journal_weather_location else 'Unknown location'

        journal_datetime = journal.find("time", {"class": "timeago"})['datetime']

        print(f"title: {journal_title}")
        print(f"text after strip: {journal_text}")
        print(f"journal_weather: {journal_real_weather}")
        print(f"journal_location: {journal_real_location}")
        print(f"journal_datetime: {journal_datetime}")
        photo_url_classes = journal.find_all('a', {"class": "photo-one"})
        photo_url_list = []
        for i, photo_url_class in enumerate(photo_url_classes):
            print(f"No.{i} photo url is: {photo_url_class.img['src']}")
            photo_url_list.append(photo_url_class.img['src'])
        
        self.save_journal(journal_title, journal_text, journal_real_weather, journal_real_location, journal_datetime, photo_url_list)
        
    def save_journal(self, title, text, weather, location, timestamp, photo_list):
        dt = dateutil.parser.isoparse(timestamp)
        save_folder_dir = os.path.join(self.save_prefix, str(dt.year), str(self.month_dict[dt.month]), str(dt.day))
        hour_minute = dt.strftime("%H:%M:%S")
        save_file_dir = f"{save_folder_dir}/{hour_minute}-{title}.md"
        print(f"save_folder_dir: {save_folder_dir}")
        if not os.path.exists(save_folder_dir):
            os.makedirs(save_folder_dir)
        try:
            with open(save_file_dir, "w") as writer:
                writer.write('## ' + title + '\n')
                writer.write(f"{self.get_font_color(self.default_time_color, dt.strftime('%H:%M:%S, %m/%d/%Y'))} \n")
                writer.write(f"{self.get_font_color(self.default_location_color, location + ', ' + weather)} \n\n")
                writer.write(text+ '\n\n')
                for idx, photo_url in enumerate(photo_list):
                    writer.write(f"![Web Photo {idx}]({photo_url})\n") # If you WANT to save images to local, comment out this line
                    writer.write(f"![Local Photo {idx}](photo_{idx}.jpg)\n") # If you DONT WANT to save images to local, comment out this line
                    open(f"{save_folder_dir}/photo_{idx}.jpg", "wb").write(requests.get(photo_url).content) # If you DONT WANT to save images to local, comment out this line
        except FileNotFoundError:
            print(save_file_dir)
            raise FileNotFoundError


        

        


