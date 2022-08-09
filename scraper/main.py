import time

from selenium.webdriver import Chrome, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import action_chains

import os
import codecs


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
    PrintButtonId = "wprm-print-button-print"
    SaveButtonXPath = "//cr-button[@class='action-button']"

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

            else:
                scrollAttempts = scrollAttempts + 1
                self.driver.execute_script("window.scrollBy(0, 250)")
                scrollDepth = scrollDepth + 250
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
        pinInfo = PinInfo(self.driver.title, pinLink)
        # time.sleep(20)
        try:
            visitor = self.driver.find_element(By.XPATH, self.PinRecipeLinkXPath)
        except:
            # Test
            print("Failed to find pin")
            # Test
            return None

        recipeLink = visitor.get_attribute('content')
        self.driver.get(recipeLink)

        try:
            printRecipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.PrintLinkText)
        except:
            try:
                recipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.JumpToRecipeLinkText)

                recipeButton.click()
                printRecipeButton = self.driver.find_element(By.PARTIAL_LINK_TEXT, self.PrintLinkText)
            except:
                print("Failed to find recipe")
                return None

        printRecipeLink = printRecipeButton.get_attribute('href')
        self.driver.get(printRecipeLink)

        # saveAsPdfButton = self.driver.find_element(By.ID, self.PrintButtonId)
        # # Test
        # print("recipe found")
        # # Test
        # saveAsPdfButton.click()

        pinInfo.pageSource = self.driver.page_source
        return pinInfo

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

    def writeHtmlToFolder(folderPath, fileName, html):
        FileHandler.makeDir(folderPath)

        fullFileName = f'{fileName}' + ".html"
        filePath = os.path.join(folderPath, fullFileName)
        if os.path.exists(filePath):
            print("Recipe already added")
            return

        f = codecs.open(filePath, "w", "utf−8")
        f.write(html)
        f.close()
        # Test
        print("Recipe written to: " + f'{folderPath}' + "/" + f'{pinInfo.name}')
        # Test

    def makeDir(folderPath):
        if os.path.exists(folderPath):
            return

        path = folderPath.split('/') or [folderPath]
        currentPath = ""
        if path[0] == "":
            path.pop(0)
            currentPath = "/"
        while len(path) != 0:
            currentPath = os.path.join(currentPath, path.pop(0))
            if not os.path.exists(currentPath):
                os.mkdir(currentPath)

    def readDictFromFile(filePath):
        if not os.path.exists(filePath):
            return dict()

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

class PinterestFileHandler(FileHandler):
    def writeFailedPinsFile(filePath, failedPinDict):
        f = open(filePath, 'w')
        for folderName, pinItems in failedPinDict.items():
            f.writelines(folderName)
            for pinItem in pinItems:
                f.writelines(pinItem.link + "\t" + pinItem.name)
            f.writelines()
        f.close()

    def readFailedPinsFile(self):
        if not os.path.exists(filePath):
            return dict()

        f = open(filePath, 'r')
        fileLines = f.readlines()
        f.close()

        pinDict = dict()
        isFolderName = True
        currentFolderName = ""
        for line in fileLines:
            if isFolderName:
                currentFolderName = line
                pinDict[currentFolderName] = []
                isFolderName = False
            elif line == "\n":
                isFolderName = True
            else:
                pinParts = line.split("\t")
                pin = PinInfo(pinParts[0], pinParts[1])
                pinDict[currentFolderName].append(pin)

        return pinDict
class PinInfo:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.pageSource = None

if __name__ == '__main__':
    homePath = "/JumperClwn"
    pinLinksExportFilePath = "pins.txt"
    failedPinLinksExportFilePath = "failed_pins.txt"
    pinsPath = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop', 'Pins')
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
        failedPinInfo = []
        for pinLink in pinLinks:
            pinInfo = pinterest.getRecipeFromPin(pinLink)
            if pinInfo is None:
                failedPinInfo.append(pinInfo)
                continue
            try:
                folderName = folderName.removesuffix("\n")
                folderPath = os.path.join(pinsPath, folderName)
                FileHandler.writeHtmlToFolder(folderPath, f'{pinInfo.name}', pinInfo.pageSource)
            except:
                failedPinInfo.append(pinInfo)
                print("Failed to write recipe")
                continue

        if len(failedPinInfo) != 0:
            failedPins[folderName] = failedPinInfo

    PinterestFileHandler.writeFailedPinsFile(failedPinLinksExportFilePath, failedPins)

    pinterest.close()
