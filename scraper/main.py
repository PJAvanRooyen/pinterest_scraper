import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from selenium.webdriver import Keys
# import os
# from bs4 import BeautifulSoup
# import re
# import urllib.request
# from selenium.webdriver.remote.webelement import WebElement

class Pin:
    def __init__(self, name, link):
        self.name = name
        self.link = link

    name = ""
    link = ""

class Folder:
    def __init__(self, name):
        self.name = name

    name = ""
    pins = []

class ChromeDriver(Chrome):
    def __init__(self, isHeadless=True):
        DRIVER_PATH = "/usr/bin/chromedriver"
        service = Service(executable_path=DRIVER_PATH)
        options = Options()
        if isHeadless:
            options.headless = isHeadless
        else:
            options.add_argument("--window-size=1920,1080")

        super(ChromeDriver, self).__init__(options=options, service=service)

class Pinterest:
    Webpage = "https://za.pinterest.com"
    FolderXPath = "//div[@data-test-id='board-section']"
    PinLinkXPath = "//*[starts-with(@href,'/pin/')]"

    def __init__(self, home = "", isHeadless=True):
        self.home = home
        self.homePath = f'{self.Webpage}' + home
        self.driver = ChromeDriver(isHeadless)

    def getAllFoldersIn(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)
        foundFolders = self.driver.find_elements(By.XPATH, self.FolderXPath)

        # TEST
        print(len(foundFolders))
        # TEST
        return foundFolders

    def getAllPinsIn(self, foundFolder):
        foundFolder.click()
        time.sleep(20)

        foundPins = []

        prevPinCount = 0
        scrollAttempts = 0
        while prevPinCount == 0 or pinCount > prevPinCount or scrollAttempts <= 3:
            self.driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(1)

            self.appendPinsFromCurrentPage(foundPins)

            pinCount = len(foundPins)
            if pinCount == prevPinCount:
                scrollAttempts = scrollAttempts + 1
            else:
                scrollAttempts = 0
                prevPinCount = pinCount

        # TEST
        print(len(foundPins))

        return foundPins

    def appendPinsFromCurrentPage(self, foundPins):
        files = self.driver.find_elements(By.XPATH, self.PinLinkXPath)
        for file in files:
            ref = file.get_attribute('href')
            if ref in foundPins:
                continue
            foundPins.append(ref)

    def getFolderName(self, foundFolder):
        name = foundFolder.get_attribute('title')
        return name

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

    #folderName = pinterest.getFolderName(folder)
    #f.write(folderName + "\n")

    f = open(pinLinksExportFilePath, 'w')
    for pin in pins:
        f.write(pin + "\n")

    pinterest.close()
