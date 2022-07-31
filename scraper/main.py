import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from selenium.webdriver import Keys
# import os
# from bs4 import BeautifulSoup
# import re
# import urllib.request
# from selenium.webdriver.remote.webelement import WebElement


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
        time.sleep(20)

        pins = []

        prevPinCount = 0
        scrollAttempts = 0
        while prevPinCount == 0 or pinCount > prevPinCount or scrollAttempts <= 3:
            self.driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(1)

            self.appendPinsFromCurrentPage(pins)

            pinCount = len(pins)
            if pinCount == prevPinCount:
                scrollAttempts = scrollAttempts + 1
            else:
                scrollAttempts = 0
                prevPinCount = pinCount

        # TEST
        print(len(pins))

        return pins

    def appendPinsFromCurrentPage(self, pins):
        files = self.driver.find_elements(By.XPATH, self.PinLinkXPath)
        for file in files:
            ref = file.get_attribute('href')
            if ref in pins:
                continue
            pins.append(ref)

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    homePath = "/JumperClwn"
    headless = False
    pinterest = Pinterest(homePath, headless)

    startFolder = "/food/"
    folders = pinterest.getAllFoldersIn(startFolder)

    folder = folders.pop()
    pins = pinterest.getAllPinsIn(folder)

    pinLinksExportFilePath = "pins.txt"
    f = open(pinLinksExportFilePath, 'w')
    for pin in pins:
        f.write(pin + "\n")

    pinterest.close()
