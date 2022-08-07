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

    def getAllFoldersIn(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)
        foundFolders = self.driver.find_elements(By.XPATH, self.FolderXPath)

        # TEST
        print(len(foundFolders))
        # TEST
        return foundFolders

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
            if title in existingFolderNames:
                continue
            existingFolderNames.append(title)
            return foundFolder

        return None


    def getAllPinsFrom(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)

        foundPins = dict()
        foundFolderNames = []

        scrollAttempts = 0
        scrollDepth = 0
        while scrollAttempts <= 3:
            currentFolder = self.findNewFolder(foundFolderNames)

            try:
                currentFolder.click()
            except:
                scrollAttempts = scrollAttempts + 1
                self.driver.execute_script("window.scrollBy(0, 250)")
                scrollDepth = scrollDepth + 250
                time.sleep(1)
                continue

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
            self.driver.get(path)
            self.driver.execute_script("window.scrollBy(0, " + f'{scrollDepth}' + ")")
            time.sleep(1)

        return foundPins

    def getAllPinsFromUsingTabs(self, folderName):
        path = f'{self.homePath}' + folderName
        self.driver.get(path)

        foundPins = dict()
        foundFolderNames = []

        scrollAttempts = 0
        newFoldersFound = False
        while not newFoldersFound and scrollAttempts <= 3:
            newFolders = self.findNewFolders(foundFolderNames)
            newFoldersFound = len(newFolders) != 0

            if not newFoldersFound:
                if scrollAttempts <= 3:
                    scrollAttempts = scrollAttempts + 1
                    self.driver.execute_script("window.scrollBy(0, 250)")
                    time.sleep(1)
                    continue
                else:
                    break

            for currentFolderName, currentFolder in newFolders.items():
                try:
                    # TODO: open in new tab
                    currentFolder.click()
                except:
                    continue

                # move to new tab
                tabs = self.driver.window_handles
                self.driver.switch_to.window(tabs[folderNumber + 1])

                # get all pins in this folder
                folderPins = self.getAllPinsIn(currentFolder)
                foundPins[currentFolderName] = folderPins
                folderNumber = folderNumber + 1
                scrollAttempts = 0

                # move back to original tab
                self.driver.driver.close();
                self.driver.driver.switch_to.window(tabs[0])

        return foundPins

    def getAllPinsIn(self, foundFolder):
        time.sleep(20)

        foundPins = []

        prevPinCount = 0
        scrollAttempts = 0
        while prevPinCount == 0 or pinCount > prevPinCount or scrollAttempts <= 3:
            self.appendPinsFromCurrentPage(foundPins)

            pinCount = len(foundPins)
            if pinCount == prevPinCount:
                scrollAttempts = scrollAttempts + 1
            else:
                scrollAttempts = 0
                prevPinCount = pinCount

            self.driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(1)

        self.driver.back()
        time.sleep(20)

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
    pinterest.getAllPinsFrom(startFolder)
    # folders = pinterest.getAllFoldersIn(startFolder)
    #
    # folder = folders.pop()
    # pins = pinterest.getAllPinsIn(folder)
    #
    # pinLinksExportFilePath = "pins.txt"
    # f = open(pinLinksExportFilePath, 'w')

    # folderName = pinterest.getFolderName(folder)
    # f.write(folderName + "\n")

    # f = open(pinLinksExportFilePath, 'w')
    # for pin in pins:
    #     f.write(pin + "\n")

    pinterest.close()
