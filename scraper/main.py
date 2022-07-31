from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# import os
# from bs4 import BeautifulSoup
# import re
# import urllib.request

class WebDriver:
    def __init__(self, headless=True):
        # Windows
        # DRIVER_PATH = os.path.join( "D:\\", "Programs", "ChromeDriver",  "chromedriver" )
        # Ubuntu
        DRIVER_PATH = "/usr/bin/chromedriver"

        service = Service(executable_path=DRIVER_PATH)

        if headless:
            options = Options()
            options.headless = headless
            options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(options=options, service=service)
        else:
            self.driver = webdriver.Chrome(service=service)

    def openPage(self, webpage='https://google.com'):
        self.driver.get(f'{webpage}')

    def findElements(self, id, value):
        return self.driver.find_elements(id, value)

    def getPage(self, webpage='https://google.com'):
        self.driver.get(f'{webpage}')
        return self.driver.page_source


class Pinterest:
    Webpage = "https://za.pinterest.com"
    FolderXPath = "//div[@data-test-id='board-section']"

    def __init__(self, home, test=False):
        self.home = home
        self.homePath = f'{self.Webpage}' + home

        self.test = test

        headless = True
        self.searcher = WebDriver(headless)

    def getAllFoldersIn(self, folder):
        path = f'{self.homePath}' + folder
        self.searcher.openPage(path)
        folders = self.searcher.findElements(By.XPATH, self.FolderXPath)
        if self.test:
            print(len(folders))


if __name__ == '__main__':
    homePath = "/JumperClwn"

    pinterest = Pinterest(homePath, True)

    folder = "/food/"
    pinterest.getAllFoldersIn(folder)
