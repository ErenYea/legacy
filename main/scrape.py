from selenium import webdriver
from selenium.webdriver.chrome import options
import time, csv
import main.constants as const
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent import futures


class Scrape(webdriver.Chrome):
    options = options.Options()
    options.headless = False
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options = webdriver.ChromeOptions()
    # options.add_argument('--log-level 3') 
    # options.headless = True
    # options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # initializing the webdriver instance
    def __init__(self, ):
        super(Scrape,self).__init__(options=self.options)
        self.result = {}
        self.state = None
        self.city = None
        self.date_from = None
        self.date_to = None
        self.count =0
        self.implicitly_wait(const.IMPLICIT_WAIT)

    # Loading the frist page
    def land_on_first_page(self):
        self.get(const.BASE_URL)


    # Selecting the country
    def select_contry(self):
        select = Select(self.find_element_by_id('ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlCountry'))
        select.select_by_visible_text('United States')
    

    # Getting the names of state
    def get_states(self):
        states = self.find_elements_by_xpath("//select[@id='ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlState']/option")
        for i in states:
            print(f"Value: {i.get_attribute('value')} , Text: {i.text}")
        # states_name = states.text.split('\n')
        # states_value = states.get_attribute('value')

        # print(states,'\n')


    # Takingt the input of state
    def input_state(self,state=''):
        select = Select(self.find_element_by_id('ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlState'))
        
        if state=='':
            self.state = 'all'
            select.select_by_value('all')
            # select.select_by_visible_text('Texas')
        else:
            self.state = state
            select.select_by_value(state)


    # Selecting the date
    def select_date(self):
        select = Select(self.find_element_by_id('ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlSearchRange'))
        select.select_by_value('88888')
    

    # Selcting the date range
    def date_range(self,date_from='02/12/2020',date_to='02/12/2021'):
        div_tag_for_date = self.find_elements_by_class_name('DateValue')
        self.date_from = date_from
        self.date_to = date_to
        print(len(div_tag_for_date))
        date_from_tag = div_tag_for_date[0].find_element_by_tag_name('input')
        date_to_tag = div_tag_for_date[1].find_element_by_tag_name('input')
        date_from_tag.clear()
        date_to_tag.clear()
        date_from_tag.send_keys(date_from)
        date_to_tag.send_keys(date_to)

    
    # Clicking on search button
    def search(self):
        search = self.find_element_by_link_text("Search")
        search.click()

    # testing the condtition of result
    def get_result(self):
        result = self.find_element_by_class_name('RefineMessage').text
        print(result)
        if '1000+' in result:
            return True
        else:
            return False
    

    # scrolling down the window to show all the results
    def scrolldown(self):
        # Get scroll height
        last_height = self.execute_script("return document.body.scrollHeight")
        print(f"last_height {last_height}")

        while True:
            # Scroll down to bottom
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # print(WebDriverWait(self, 20
            #     ).until(EC.presence_of_element_located((By.XPATH, '//div[@class="Listings"]/img'))))
            # print(WebDriverWait(self, 20
            #     ).until_not(EC.presence_of_element_located((By.XPATH, '//div[@class="Listings"]/img'))))
            # Wait to load page
            time.sleep(const.SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.execute_script("return document.body.scrollHeight")
            print(f"new_height {new_height}")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"last_height {last_height}")
    
    def result_to_csv(self,name='result.csv'):
        result = self.find_element_by_xpath('//div[@class="Obituaries"]')
        results = self.find_elements_by_xpath('//div[@class="mainScrollPage"]')
        with open(name,'w',newline='',encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            
            for i in results:
                a = i.find_elements_by_class_name('entryContainer')
                print(len(a))
                for j in a:
                    s=j.find_element_by_class_name("obitName")
                    h = s.find_element_by_tag_name('a')
                    print(f"TExt: {s.text}  link: {h.get_attribute('href')}")
                    csv_writer.writerow([s.text,h.get_attribute('href')])
                    self.result[s.text] = h.get_attribute('href')
                    # self.result.append([s.text,h.get_attribute('href')])
                    print("\n")
        self.close()

    def read_result(self,key):
        driver= webdriver.Chrome(options=self.options)
        # self.count += 1
        # self.execute_script("window.open('');")
        # self.switch_to.window(self.window_handles[self.count])

        url = self.result[key]
        print(f"Extracting Data about {key}")
        try:    
            driver.get(url)
            driver.implicitly_wait(10)
            if 'legacy.com' in driver.current_url:
                try:

                    element= driver.find_element_by_xpath("//div[@class='Box-sc-5gsflb-0 iobueB']/div[2]/div")
                    print(element.text)
                    # i+=1
                    print('\n')
                    # print(i)
                    # print('\n')
                except:
                    print('\n\n')
                    print("cannot find element")
                    print('\n')
            else:
                return
        except:
            print('Url deneid')
            print('\n')
        driver.close()
        # self.switch_to.window(self.window_handles[0])

    def runscrapper(self):
        with futures.ThreadPoolExecutor() as executor:
            # store the url for each thread as a dict, so we can know which thread fails
            future_results = {key: executor.submit(self.read_result,key) for key in self.result}
            # print(future_results)
            for key, future in future_results.items():
                try:
                    # print(key,future)
                    future.result()  # can use `timeout` to wait max seconds for each thread
                except Exception as exc:  # can give a exception in some thread
                    print('url {:0} generated an exception: {:1}'.format(key, exc))
        # return results
