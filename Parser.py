import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


class CopartParse:
    def __init__(self, url, count_page=100):
        self.url = url
        self.count_page = count_page
        self.number_of_page = 0
        self.data = None

    def __set_up(self):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        self.driver = uc.Chrome(options=options)

    def __get_url(self):
        self.driver.get(self.url)

    def __paginator(self):
        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, '[class="p-paginator-icon pi pi-angle-right"]')))
        while self.driver.find_elements(By.CSS_SELECTOR, '[class="p-paginator-icon pi pi-angle-right"]') and self.count_page > self.number_of_page:
            self.__parse_page()
            
            self.number_of_page += 1

            if self.number_of_page == self.count_page:
                break

            for i in range(self.number_of_page):
                WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, '[class="p-paginator-icon pi pi-angle-right"]')))
            
                self.driver.find_element(By.CSS_SELECTOR, '[class="p-paginator-icon pi pi-angle-right"]').click()
            
                time.sleep(2)

            
    def __parse_page(self):

        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((
                By.CSS_SELECTOR, '[class="p-element p-selectable-row ng-star-inserted"]')))

        titles = self.driver.find_elements(By.CSS_SELECTOR, '[class="p-element p-selectable-row ng-star-inserted"]')

        urls = [title.find_element(By.CSS_SELECTOR, '[class="search_result_lot_detail_meta_data_block"]').
                find_element(By.CSS_SELECTOR, '[class="ng-star-inserted"]').get_attribute('href') for title in titles]

        for url in urls:
                
                self.driver.get(url)
                
                try:
                    WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, '[class="lot-details-section vehicle-info"]')))
                    
                    new_car = dict()
                    
                    if self.driver.find_elements(By.CSS_SELECTOR, '[class="lot-details-section vehicle-info"]'):
                        base_info = self.driver.find_element(By.CSS_SELECTOR, '[class="lot-details-section vehicle-info"]').text
                        base_info = base_info.split()
                
                        new_car['lot_number'] = int(base_info[base_info.index('лота:')+1])
                        new_car['miles'] = float(base_info[base_info.index('Одометр:')+1].replace(',', '.'))
                        new_car['transmission'] = base_info[base_info.index('Передача:')+1]
                        new_car['fuel'] = base_info[base_info.index('Топливо:')+1]
                        new_car['drive'] = base_info[base_info.index('Привод:')+1]
                        
                    if self.driver.find_elements(By.CSS_SELECTOR, '[class="p-m-0"]'):    
                        new_car['name'] = self.driver.find_element(By.CSS_SELECTOR, '[class="p-m-0"]').text
                    
                    if self.driver.find_elements(By.CSS_SELECTOR, '[class="ldt5-full-vehicle-details-section"]'):
                        more_info = self.driver.find_element(By.CSS_SELECTOR, '[class="ldt5-full-vehicle-details-section"]').text
                        more_info = more_info.split()
                        
                        new_car['make'] = more_info[more_info.index("Марка:")+1]
                        new_car['year'] = int(more_info[more_info.index("Год:")+1])
                    
                    if self.driver.find_elements(By.CSS_SELECTOR, '[class="p-border-bottom-dark-gray-3 p-cursor-pointer p-position-relative"]'):
                        new_car['auction'] = self.driver.find_element(By.CSS_SELECTOR, '[class="p-border-bottom-dark-gray-3 p-cursor-pointer p-position-relative"]').text
                    
                    self.data = self.data._append(new_car, ignore_index=True)
                
                except:
                    continue
 
        self.driver.get(self.url)



    def parse(self, data=None):
        if data:
            self.data = data
        else:
            self.data = pd.DataFrame()
        
        try:
            self.__set_up()
            self.__get_url()
            self.__paginator()
        finally:
            self.quit()

    def quit(self):
        self.driver.quit()

