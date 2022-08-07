import time

from selenium.webdriver import Chrome, Keys
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
    FolderButtonXPath = "//div[@role='button' and @tabindex='0']/parent::div[@data-test-id='board-section']"

    def __init__(self, home="", isHeadless=True):
        self.home = home
        self.homePath = f'{self.Webpage}' + home
        self.driver = ChromeDriver(isHeadless)

    def getAllPinsFrom(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)

        foundFolderNames = []
        prevFoundFolderCount = 0
        foundPins = dict()

        scrollAttempts = 0
        scrollDepth = 0
        while scrollAttempts <= 3:
            currentFolder = self.findNewFolder(foundFolderNames)

            foundFolderCount = len(foundFolderNames)
            if foundFolderCount > prevFoundFolderCount:
                prevFoundFolderCount = foundFolderCount

                try:
                    currentFolder.click()
                    time.sleep(20)
                except:
                    break

                foundFolderName = foundFolderNames[-1]

                # Test
                print("Folder Found: " + f'{foundFolderName}')
                # Test

                # get all pins in this folder
                folderPins = self.getAllPinsIn(currentFolder)
                foundPins[foundFolderName] = folderPins
                scrollAttempts = 0

                # Test
                print("No. of pins found: " + f'{len(folderPins)}')
                # Test

                # move back to original tab
                self.driver.back()
                self.driver.execute_script("window.scrollBy(0, " + f'{scrollDepth}' + ")")
                time.sleep(1)

            else:
                scrollAttempts = scrollAttempts + 1
                self.driver.execute_script("window.scrollBy(0, 250)")
                scrollDepth = scrollDepth + 250
                time.sleep(1)
                continue

        return foundPins

    def findNewFolders(self, existingFolderNames):
        newFolders = dict()

        folders = self.driver.find_elements(By.XPATH, self.FolderButtonXPath)
        for folder in folders:
            title = folder.text
            if title in existingFolderNames:
                continue
            existingFolderNames.append(title)
            newFolders[title] = folder

        return newFolders

    def findNewFolder(self, existingFolderNames):
        foundFolders = self.driver.find_elements(By.XPATH, self.FolderButtonXPath)
        for foundFolder in foundFolders:
            title = foundFolder.text
            name = title.split(sep="\n")
            name = name[0]
            if name in existingFolderNames:
                continue
            existingFolderNames.append(name)
            return foundFolder

        return None

    def getAllPinsIn(self, foundFolder):
        foundPins = []

        prevPinCount = 0
        scrollAttempts = 0
        while prevPinCount == 0 or pinCount > prevPinCount or scrollAttempts <= 3:
            self.appendPinsFromCurrentPage(foundPins)

            pinCount = len(foundPins)
            if pinCount == prevPinCount:
                scrollAttempts = scrollAttempts + 1
                self.driver.execute_script("window.scrollBy(0, 250)")
                time.sleep(1)
            else:
                scrollAttempts = 0
                prevPinCount = pinCount

        return foundPins

    def appendPinsFromCurrentPage(self, foundPins):
        files = self.driver.find_elements(By.XPATH, self.PinLinkXPath)
        for file in files:
            ref = file.get_attribute('href')
            if ref in foundPins:
                continue
            foundPins.append(ref)

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    homePath = "/JumperClwn"
    headless = False
    pinterest = Pinterest(homePath, headless)

    startFolder = "/food/"
    pins = pinterest.getAllPinsFrom(startFolder)

    pinLinksExportFilePath = "pins.txt"
    f = open(pinLinksExportFilePath, 'w')

    for nameOfFolder, pinLinks in pins.items():
        f.write(nameOfFolder + "\n")
        for pinLink in pinLinks:
            f.write(pinLink + "\n")
        f.write("\n")

    pinterest.close()
