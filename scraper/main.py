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
    PinRecipeLinkXPath = "//meta[@property='pinterestapp:source']"
    DownloadButtonId = "wprm-print-button-print"

    PrintLinkText = "Print"
    JumpToRecipeLinkText = "Jump to Recipe"

    def __init__(self, home="", isHeadless=True):
        self.home = home
        self.homePath = f'{self.Webpage}' + home
        self.driver = ChromeDriver(isHeadless)
        self.driver.implicitly_wait(20)

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
                    # time.sleep(20)
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
                # time.sleep(1)

            else:
                scrollAttempts = scrollAttempts + 1
                self.driver.execute_script("window.scrollBy(0, 250)")
                scrollDepth = scrollDepth + 250
                # time.sleep(1)
                continue

        return foundPins

    def findNewFolders(self, existingFolderNames):
        newFolders = dict()

        folders = self.driver.find_elements(By.XPATH, self.FolderXPath)
        for folder in folders:
            title = folder.text
            if title in existingFolderNames:
                continue
            existingFolderNames.append(title)
            newFolders[title] = folder

        return newFolders

    def findNewFolder(self, existingFolderNames):
        foundFolders = self.driver.find_elements(By.XPATH, self.FolderXPath)
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
                # time.sleep(1)
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

    def getRecipeFromPin(self, pinLink):
        self.driver.get(pinLink)
        # time.sleep(20)
        try:
            visitor = self.driver.find_element(By.XPATH, self.PinRecipeLinkXPath)
            # Test
            print("Pin page found")
            # Test
        except:
            # Test
            print("Failed to find pin page")
            # Test
            return False

        recipeLink = visitor.get_attribute('content')
        self.driver.get(recipeLink)

        try:
            printRecipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.PrintLinkText)
            # Test
            print(f'{printRecipeButton.text}' + " button found")
            # Test
        except:
            try:
                recipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.JumpToRecipeLinkText)

                recipeButton.click()
                printRecipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.PrintLinkText)
                # Test
                print(f'{printRecipeButton.text}' + " button found")
                # Test
            except:
                print("Failed to find recipe")
                return False

        printRecipeLink = printRecipeButton.get_attribute('href')
        self.driver.get(printRecipeLink)

        saveAsPdfButton = self.driver.find_element(By.ID, self.DownloadButtonId)
        # Test
        print(f'{saveAsPdfButton.text}' + " button found")
        # Test
        saveAsPdfButton.click()
        return True

    def close(self):
        self.driver.close()

class FileHandler:
    def writeDictToFile(filePath, dictionary):
        f = open(filePath, 'w')
        for key, values in dictionary.items():
            f.writelines(key)
            for value in values:
                f.writelines(value)
            f.writelines()
        f.close()

    def readDictFromFile(filePath):
        f = open(filePath, 'r')
        fileLines = f.readlines()
        f.close()

        dictionary = dict()
        isKey = True
        currentKey = ""
        for line in fileLines:
            if isKey:
                currentKey = line
                dictionary[currentKey] = []
                isKey = False
            elif line == "\n":
                isKey = True
            else:
                dictionary[currentKey].append(line)

        return dictionary

if __name__ == '__main__':
    homePath = "/JumperClwn"
    pinLinksExportFilePath = "pins.txt"
    failedPinLinksExportFilePath = "failed_pins.txt"
    headless = False
    pinterest = Pinterest(homePath, headless)

    searchForPins = False
    getRecipesFromFailedPins = False

    filePath = pinLinksExportFilePath
    if getRecipesFromFailedPins:
        filePath = failedPinLinksExportFilePath
    pins = FileHandler.readDictFromFile(filePath)

    # TODO: add pins from file to search to only obtain new pins
    if searchForPins:
        startFolder = "/food/"
        pins = pinterest.getAllPinsFrom(startFolder)

        FileHandler.writeDictToFile(pinLinksExportFilePath, pins)

    # Now we have the new pins, open them and save their content.
    failedPins = dict()
    for folderName, pinLinks in pins.items():
        failedPinLinks = []
        for pinLink in pinLinks:
            if pinterest.getRecipeFromPin(pinLink):
                continue
            failedPinLinks.append(pinLink)

        if len(failedPinLinks) != 0:
            failedPins[folderName] = failedPinLinks

    FileHandler.writeDictToFile(failedPinLinksExportFilePath, failedPins)

    pinterest.close()
