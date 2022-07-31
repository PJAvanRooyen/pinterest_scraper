import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# import os
# from bs4 import BeautifulSoup
# import re
# import urllib.request
from selenium.webdriver.remote.webelement import WebElement


class Pinterest:
    Webpage = "https://za.pinterest.com"
    FolderXPath = "//div[@data-test-id='board-section']"
    PinLinkXPath = "//*[starts-with(@href,'/pin/')]"

    def __init__(self, home, headless=True):
        self.home = home
        self.homePath = f'{self.Webpage}' + home

        DRIVER_PATH = "/usr/bin/chromedriver"
        service = Service(executable_path=DRIVER_PATH)
        if headless:
            options = Options()
            options.headless = headless
            options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(options=options, service=service)
        else:
            self.driver = webdriver.Chrome(service=service)

    def getAllFoldersIn(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)
        folders = self.driver.find_elements(By.XPATH, self.FolderXPath)

        # TEST
        print(len(folders))
        # TEST
        return folders

    def getAllPinsIn(self, folder):
        folder.click()
        time.sleep(10)

        prevFileCount = 0
        files = self.driver.find_elements(By.XPATH, self.PinLinkXPath)
        fileCount = len(files)
        while fileCount > prevFileCount:
            prevFileCount = fileCount
            self.driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(1)

            newFiles = self.driver.find_elements(By.XPATH, self.PinLinkXPath)
            for file in newFiles:
                if file in files:
                    continue
                files.append(file)

            fileCount = len(files)

        # TEST
        print(len(files))

        return files

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    homePath = "/JumperClwn"

    headless = False
    pinterest = Pinterest(homePath, headless)

    startFolder = "/food/"
    folders = pinterest.getAllFoldersIn(startFolder)

    pins = pinterest.getAllPinsIn(folders.pop())

    # for folder in folders:
    #     files = pinterest.getAllPinsIn(folder)

    pinterest.close()
