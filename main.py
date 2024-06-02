from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

from bs4 import BeautifulSoup
import time
import regex as re

# Format of URL "https://www.google.com/maps/search/insert+your+data+here
# eg. url = "https://www.google.com/maps/search/doctors+in+LA"

class Scrapper:
    browser = None
    actions = None

    page_tag = "k7jAl miFGmb lJ3Kh PLbyfe" 
    places_name_href_tag = "hfpxzc"

    # Tried Using Tags Class name but was Not able to make it work.... idk why ?
    places_name_tag = "DUwDvf lfPIob"
    # Contains -> Address ; Webiste ; Menu ; Phone No ; Plus Code ; "Send To Phone"
    places_description_tags = "Io6YTe fontBodyMedium kR99db"
    places_reviews_tag = "fontDisplayLarge"


    # So using XPATHS now :
    places_name_xpath_tag = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1'
    places_description_xpath_tags = ''
    places_reviews_xpath_tag = ''

    

    max_places_names = 35 # Change the max number of places info to load according to your need

    places_name_list = []
    places_ph_no_list = []
    places_address_list = []
    places_time_open_list = []
    places_ratings_stars_list = []
    places_website_list = []

    def init(self):
        # Creating the Browser Headless
        options = Options()
        options.add_argument('--headless=new')

        # Creating an instance of browser
        self.browser = webdriver.Chrome("chromedriver.exe", options=options)

        # Creates "Actions" in a way maybe mimics user Behaviour
        self.actions = ActionChains(self.browser) 
    
    def is_phone_number(self,item):
        # The pattern ^\+?(\d[\d\s\-]{9,}\d)$ matches phone numbers 
        #       that may start with a + sign, 
        #       followed by digits, spaces, or hyphens, ensuring a minimum length of digits.
        phone_pattern = re.compile(r'^\+?(\d[\d\s\-]{9,}\d)$')
        return bool(phone_pattern.match(item))

    def scrap(self, url:str):
        self.init()
        self.browser.get(url)
        # Checks if the Sidebar of the page was Loaded or Not 
        # WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, self.page_tag)))
        time.sleep(3)

        # Get all the laoded "Places"
        side_bar_tags = self.browser.find_elements(By.CLASS_NAME, self.places_name_href_tag)

        # Load other "Places" atleast 35
        length_of_tagline = len(side_bar_tags)

        # Scroll untill 35 places or no new places left
        while length_of_tagline <= self.max_places_names:
            print(f"Number of Places: {length_of_tagline}")
            scroll_origin = ScrollOrigin.from_element(side_bar_tags[-1], 100)
            self.actions.scroll_from_origin(scroll_origin, 0, 100).perform()
            time.sleep(2)

            side_bar_tags = self.browser.find_elements(By.CLASS_NAME, self.places_name_href_tag)
            
            # If all places are discovered
            if len(side_bar_tags) == length_of_tagline :
                break

            length_of_tagline = len(side_bar_tags)

        print(f"{length_of_tagline} Total Places Found...")
        
        for tag in side_bar_tags:
            # scroll_origin = ScrollOrigin.from_element(tag)
            try:
                self.actions.scroll_to_element(tag).perform()
                self.actions.move_to_element(tag).perform()
                self.actions.click(tag).perform()
            except Exception as exp:
                print(f"Excpetion Occured: {exp}")

            time.sleep(3)
            # Parse it through Beutifull Soup because Normal Selenium Wait :
            # [WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, self.places_name_tag)))] is Not Working 
            # or Maybe I am Using the Wrong Locator... 
            source = self.browser.page_source
            soup = BeautifulSoup(source, 'html.parser')

            name_element = soup.find_all('h1', {'class': self.places_name_tag})
            # # name_element = self.browser.find_element(By.CLASS_NAME, self.places_name_tag)
            # name_element = self.browser.find_element(By.XPATH, self.places_name_xpath_tag)
            name = name_element[0].text
            if name not in self.places_name_list:
                self.places_name_list.append(name)
                phone = None
                website = None
                address = None

                desc_divs = soup.findAll('div', {"class": self.places_description_tags})
                if desc_divs is not None:
                    address = desc_divs[0].text
                    for div in desc_divs:
                        content = div.text
                        if website == None and content[-3] == '.' :
                            website = content
                        elif phone == None and self.is_phone_number(content):
                            phone = content
                
                address = "Not Available" if address is None else address
                website = "Not Available" if website is None else website
                phone = "Not Available" if phone is None else phone
                self.places_address_list.append(address)
                self.places_website_list.append(website)
                self.places_ph_no_list.append(phone)

                print(f"{name}  |  {address}  |  {website}  |  {phone}")                        

        print(f"Total Places: {len(self.places_name_list)}")
        print(self.places_name_list)

        
if __name__ == '__main__':
    print("     Hello World !     ")
    print("--- Google Maps Scrapper ---")

    search_prompt = input("Enter Your Prompt Here > ")
    # url = "https://www.google.com/maps/search/" + search_prompt.replace(" ", "+")
    url = "https://www.google.com/maps/search/doctors+in+ghandhinagar"
    print(f"URL is: {url}")
    scrap_obj = Scrapper()
    scrap_obj.scrap(url=url)