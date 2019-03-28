# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from bs4 import BeautifulSoup
from requests import get, post, patch
import html5lib
import datetime
import json
import traceback
from abc import ABC, abstractmethod

class ReviewSnippet:
    
    def __init__(self, phone, source, category, reviewText, reviewurl):
        self.phonename = phone
        self.sourcename = source
        self.category = category
        self.reviewtext = reviewText
        self.reviewurl = reviewurl
        
    def printReview(self):
        #printString = ''{} {} review from {}'.format(self.phone, self.category, self.source))
        print("-------------------------------------")
        print(self.phonename + " " + self.category + " review from " + self.sourcename)
        print(self.reviewtext)
        print("-------------------------------------")
        
class PhoneInfo:
    
    def __init__(self, phone, price=None, score=None, imageurl=None):
        self.phonename = phone
        self.price = price
        self.score = score
        self.imageurl = imageurl
        
class DatabaseInteract:
    
        def __init__(self):
            username = "test@test.com"
            password = "test"

            r = post("https://ehl.me/api/login", json={"username": username, "password": password})
            
            self.token = r.text
    
        def postReviews(self, reviewList):
            try:
                headers = {"Authorization": "Bearer " + self.token}
                p = post("https://ehl.me/api/review", json=reviewList, headers=headers)
            except Exception as e:
                print(e.args)
            else:
                print(p.text)
                print(p.status_code)
            
        def postPhonesList(self, phonenamesList):
            try:
                headers = {"Authorization": "Bearer " + self.token}
                p = post("https://ehl.me/api/phones", json=phonesnamesList, headers=headers)
            except Exception as e:
                print(e.args)
            else:
                print(p.text)
                print(p.status_code)
            
        def postPhoneInfo(self, phone):
            if phone is None:
                print("No Phone")
                return
            try:
                headers = {"Authorization": "Bearer " + self.token}
                p = patch("https://ehl.me/api/phone", json=phone, headers=headers)
            except Exception as e:
                print(e.args)
            else:
                print(p.text)
                print(p.status_code)

class Category(ABC):
    
    def __init__(self):
        self.name = NotImplemented
        self.components = []
        
        self.checkList = []
        self.initializeGeneralChecks()
        
    def getComponents(self):
        return self.components
    
    def addComponent(self, newComponent):
        self.components.append(newComponent)
    
    def getCheckList(self):
        return self.checkList
    
    def addToChecklist(self, newItem):
        self.checkList.insert(0, newItem)
    
    def getName(self):
        return self.name
    
    def setName(self, newName):
        self.name = newName
    
    def initializeGeneralChecks(self):
        self.checkList.append('better')
        self.checkList.append('great')
        self.checkList.append('good')
        self.checkList.append('fine')
        self.checkList.append('bad')
        self.checkList.append('worse')
        self.checkList.append('awful')
        self.checkList.append('terrible')
    


    
class Battery(Category):

    def __init__(self):
        super().__init__()
        self.setName('battery')
        
        self.components.append('battery')
        self.components.append('battery life')
        
        # These are battery specific, and hence more likely. Finding them first
        # saves processing time
        self.checkList.insert(0, 'long')
        self.checkList.insert(0, 'short')
        self.checkList.insert(0, 'hours')


class Camera(Category):
    def __init__(self):
        super().__init__()
        self.name = 'camera'
        self.components.append('camera')
        
        self.checkList.insert(0, 'megapixel')
        
class Performance(Category):
    def __init__(self):
        super().__init__()
        self.setName('performance')
        self.components.append('performance')
        self.components.append('processor')
        
        
        self.checkList.insert(0, 'fast')
        self.checkList.insert(0, 'slow')
        self.checkList.insert(0, 'speed')
        
class Display(Category):
    def __init__(self):
        super().__init__()
        self.setName('display')
        self.components.append('display')
        self.components.append('screen')
        
        
        self.checkList.insert(0, 'resolution')
        self.checkList.insert(0, 'ppi')
        self.checkList.insert(0, 'bright')
        self.checkList.insert(0, 'dim')
        self.checkList.insert(0, 'colorful')
        

class Scraper(ABC):
    
    def soupFromUrl(self, url, parser='html.parser'):
        # DO ERROR HANDLING
        #1. no response (exception)
        #2. response but not successful
        #3. response successful but data incorrect (i guess thats for something else?)
        
        response = get(url)
        
        if response.ok:
            return BeautifulSoup(response.text, parser)
        else:
            raise RuntimeError("Status code: " + str(response.status_code))
    
    def getAllContent(self, soup, htmlTag, additionalInfoDict=None):
        if additionalInfoDict is None:
            content = soup.find_all(htmlTag)
        else:
            content = soup.find_all(htmlTag, additionalInfoDict)
        
        
        assert (len(content) > 0), ("Soup Content " + self.getSoupErrorMessage(htmlTag, additionalInfoDict) + \
                " was not found for " + self.getPhone() + " from " + self.getSourceForErrorMessage() + \
                ". Check HTML tags of source website for this phone") 

        return content
            
    def getContent(self, soup, htmlTag, additionalInfoDict=None):
        if additionalInfoDict is None:
            content = soup.find(htmlTag)
        else:
            content = soup.find(htmlTag, additionalInfoDict)
            
        assert content is not None, ("Soup Content " + self.getSoupErrorMessage(htmlTag, additionalInfoDict) + \
                                     " was not found for " + self.getPhone() + " from " + self.getSourceForErrorMessage() + \
                                     ". Check HTML tags of source website for this phone") 
        
        return content
    
    def getLink(self, soup):
        content = soup.find('a', href=True)
        
        assert content is not None, ("Soup Content " + self.getSoupErrorMessage() + \
                                     " was not found for " + self.getPhone() + " from " + self.getSourceForErrorMessage() + \
                                     ". Check HTML tags of source website for this phone") 
        
        return content
    
    def getLinks(self, soup):
        content = soup.find_all('a', href=True)
        
        assert (len(content) > 0), ("Soup Content " + self.getSoupErrorMessage() + \
                " was not found for " + self.getPhone() + " from " + self.getSourceForErrorMessage() + \
                ". Check HTML tags of source website for this phone") 
        
        return content
    
    def getSourceForErrorMessage(self):
        return "source not defined"
    
    def getSoupErrorMessage(self, htmlTag='a', additionalInfoDict=None):
        if additionalInfoDict is None:
            return htmlTag
        else:
            return htmlTag + " " + str(additionalInfoDict)
        
        
    def sendWarning(self, message):
        print(message)
        
    def getImage(self):
        bingSearchUrl = "https://www.bing.com/images/search?q=" + self.getPhone().replace(" ", "+")
        print(bingSearchUrl)
        bingImageResults = self.soupFromUrl(bingSearchUrl, parser='html5lib')
        #print(bingImageResults)
        
        images = self.getAllContent(bingImageResults, 'a')
        for imag in images:
            if "www.bing.com" in imag['href']:
                print(imag['href'])
            else: print(imag)           

    def googleUrlFixer(self, url):
        return url.split("=", 1)[-1].split("&", 1)[0]
    
    


class PhoneScraper(Scraper):    
    def __init__(self, phoneId):
        self.source = NotImplemented
        self.phone = phoneId
        self.reviewUrl = None
        
        battery = Battery()
        display = Display()
        camera = Camera()
        performance = Performance()
    
        #self.categories = [battery]#, display, processor]
        self.categories = [battery, display, camera, performance]
        self.reviews = []
        
    @abstractmethod
    def scrape(self, soup):
        pass
    
    @abstractmethod
    def getSourceReview(self):
        pass
    
    def getSourceForErrorMessage(self):
        reviewUrl = self.getReviewUrl()
        if reviewUrl is not None:
            return reviewUrl
        else:
            return self.getSource()
    
    def getReview(self):
        review = self.getSourceReview()
        if review is None:
            errorMessage = "No review results found for " + self.getPhone() + " from " + self.getSource() + \
            ". Check phone and source name, and make sure source has a review for that phone."
            self.sendWarning(errorMessage)
            raise RuntimeError(errorMessage) 
        else:
            return review
    
    def getSource(self):
        return self.source
    
    def setSource(self, newSource):
        self.source = newSource
    
    def getPhone(self):
        return self.phone
    
    def getPhoneInfo(self):
        return None
    
    def setReviewUrl(self, reviewUrl):
        self.reviewUrl = reviewUrl
    
    def getReviewUrl(self):
        return self.reviewUrl
    
    def getCategories(self):
        return self.categories
    
    def categorizeText(self, text):
        # looks at the text of a review. if the text fits a category (through the categoryList),
        # it checks if the text is valid for the category (through the checkList)
        compareText = text.lower()
        checkFlag = False
        for cat in self.getCategories():
            for comp in cat.getComponents():
                if comp in compareText:
                    checkFlag = True
                    break
            
            if checkFlag:
                for checkItem in cat.getCheckList():
                    if checkItem in compareText:
                        reviewCategory = cat.getName()
                        self.addReview(reviewCategory, text) #PLUS WHATEVER OTHER INFO
                        break
                checkFlag = False
                
    def addReview(self, category, text):
        newSnippet = ReviewSnippet(self.getPhone(), self.getSource(), category, text, self.getReviewUrl())
        self.reviews.append(newSnippet)
        

        
        
        
#         resultsDivs = self.getAllContent(bingImageResults, 'div', {'class' : 'vm_c'})
#         #print(resultsDivs)
#         firstResult = None
#         for div in resultsDivs:
#             try:
#                 firstResult = self.getContent(resultsDiv, 'img')
#             except:
#                 pass
        
#         print(firstResult)
        
        

    
    
class VergeScraper(PhoneScraper):
    
    def __init__(self, phoneId):
        super().__init__(phoneId)
        self.setSource('TheVerge')
    
    def scrape(self, soup):
        content = self.getAllContent(soup, 'div', {'class':'c-entry-content'})
        
        for cont in content:
            paragraphs = self.getAllContent(cont, 'p')
            for para in paragraphs:
                self.categorizeText(para.text)
                
    def getSourceReview(self):
        urlString = self.getSource() + "+" + self.getPhone().replace(" ", "+") + "+review"
        url = 'https://www.google.com/search?q=' + urlString
        

        searchSoup = self.soupFromUrl(url)


        searchResults = self.getAllContent(searchSoup, 'div', {'id':'ires'})
        checkText = self.getPhone() + " review"
        for result in searchResults:
            for a in self.getLinks(result):
                if (checkText in a.text.lower()):
                    link = a['href']
                    if ("www." + self.getSource().lower() + ".com") in link:
                        link = self.googleUrlFixer(link)
                        
                        self.setReviewUrl(link)
                        return self.soupFromUrl(link)
                        
        
        return None
            

                

class TechRadarScraper(PhoneScraper):
    
    def __init__(self, phoneId):
        super().__init__(phoneId)
        self.setSource('TechRadar')
    
    def scrape(self, soup):
        self.pageScrape(soup)
        pageBar = self.getContent(soup, 'div', {'class' : 'swipe-pages-container'})
        listItems = self.getAllContent(pageBar, 'li') 
        for item in listItems:
            for a in self.getLinks(item):
                innerSoup = self.soupFromUrl(a['href'])
                self.pageScrape(innerSoup)
        

        
    def pageScrape(self, soup):
        content = soup.find_all('div', {'itemprop':'reviewBody'})
        
        for cont in content:
            paragraphs = self.getAllContent(cont, 'p')
            for para in paragraphs:
                self.categorizeText(para.text)
                
    def getSourceReview(self):
        phoneUrlString = self.getPhone().replace(" ", "+")
        
        url = "https://www.techradar.com/search?searchTerm=" + phoneUrlString + "review"
        
        searchSoup = self.soupFromUrl(url)

        checkText = self.getPhone() + " review"
        
        try:
            searchResults = self.getAllContent(searchSoup, 'div', {'class':'listingResult'})
        except:
            self.sendWarning("No Techradar reviews found for " + self.getPhone())
        else:
            for result in searchResults:
                header = self.getContent(result, 'header')
                if (checkText in header.text.lower()):
                        a = self.getLink(result)
                        link = a['href']
                        self.setReviewUrl(link)
                        return self.soupFromUrl(link)
                
        return None
            
                

class CnetScraper(PhoneScraper):
    
    def __init__(self, phoneId):
        super().__init__(phoneId)
        self.setSource('Cnet')
        self.rootSourceUrl = "https://www.cnet.com"
        self.price = None
        self.rating = None
        self.imageUrl = None
        
    def getPrice(self):
        return self.price
    
    def setPrice(self, newPrice):
        self.price = newPrice
    
    def getRating(self):
        return self.rating
    
    def setRating(self, newRating):
        self.rating = newRating
        
    def getImageUrl(self):
        return self.imageUrl
    
    def setImageUrl(self, newImageUrl):
        self.imageUrl = newImageUrl
    
    def getPhoneInfo(self):
        return PhoneInfo(self.getPhone(), self.getPrice(), self.getRating(), self.getImageUrl())
    
    def pageScrape(self, soup):
        
        content = self.getAllContent(soup, 'div', {'id':'editorReview'})
        for cont in content:
            paragraphs = self.getAllContent(cont, 'p')
            for para in paragraphs:
                self.categorizeText(para.text)
                
    
    def scrape(self, soup):
        self.pageScrape(soup)
        self.determinePrice(soup)
        self.determineRating(soup)
        self.determineImage(soup)
        navLinks = self.getAllContent(soup, 'div', {'class':'pageNav'})
        for navLink in navLinks:
            for a in self.getLinks(navLink):
                innerSoup = self.soupFromUrl(self.rootSourceUrl + a['href'])
                self.pageScrape(innerSoup)
        
    
    def getSourceReview(self):
        phoneUrlString = self.getPhone().replace(" ", "%20")
        url = "https://www.cnet.com/search/?query=" + phoneUrlString + "%20review&page=1"
        
        searchSoup = self.soupFromUrl(url)

        try:
            searchResults = self.getAllContent(searchSoup, 'div', {'class':'col-4 itemInfo'})
        except:
            self.sendWarning("No Cnet review found for " + self.getPhone())
        else:
            for result in searchResults:
                for a in self.getLinks(result):
                    if (self.getPhone() in a.text.lower()):
                        link = self.rootSourceUrl + a['href']
                        if "preview" in link:
                            continue
                        else:
                            self.setReviewUrl(link)
                            return self.soupFromUrl(link)
        
        return None
                
    def determinePrice(self, pageSoup):
        try:
            content = self.getContent(pageSoup, 'div', {'class':'price'})
        except:
            self.sendWarning("Price not found for " + self.getPhone() + " " + self.getSource() )
            return
            
        
        a = self.getLink(content)
        price = a.text
        price = price.replace("$", " ")
        
        decimalIndex = price.index(".")
        price = price[:decimalIndex+2]
        
        
        self.setPrice(float(price))
        print("Price is" + price)
        
    def determineRating(self, pageSoup):
        ratingString = self.getContent(pageSoup, 'div', {'class' : 'innerRating'}).text
        rating = float(ratingString.split(" ")[0])
        self.rating = rating
        
    def determineImage(self, pageSoup):
        
        try:
            content = self.getContent(pageSoup, 'div', {'class': 'videoStill'})
        except Exception as e:
            self.sendWarning(e.args)
        else:
             self.setImageUrl((content['style'].split('(')[1].split(')')[0]))
             return
         
        try: 
            self.getContent(pageSoup, 'div', {'id':'editorReview'})
        except Exception as e:
            self.sendWarning(e.args)
        else:
            self.setImageUrl(self.getContent(content, 'img')['src'])
            
        
            
         
        #content = self.getContent(pageSoup, 'div', {'id':'editorReview'})
        #content = self.getContent(pageSoup, 'div', {'class':'shortcode'})
        #content = self.getContent(pageSoup, 'div', {'class': 'videoStill'})
        #print(self.getContent(content, 'img')['src'])
        #print(content['style'].split('(')[1].split(')')[0])
                
        
            
        

class PhoneListScraper(Scraper):
    
    def __init__(self):
        self.excludeDict = {} #String to list
        self.excludeDict["samsung galaxy"] = ["samsung "]
    
    def getExcludeKeys(self):
        return self.excludeDict.keys()
    
    def getExcludeValue(self, key):
        return self.excludeDict[key]
    
    def removeYears(self, string):
        if "(" in string:
            endIndex = string.index("(")
            string = string[:endIndex-1] #remove last space as well
        return string            
    
    def fixString(self, string):
        string = self.removeYears(string)
        for key in self.getExcludeKeys():
            if key in string:
                for excludeString in self.getExcludeValue(key):
                    string = string.replace(excludeString, "")
        return string
    
    def getPhones(self, year):
        phoneList = []
        currentYear = str(year)
        wikiUrl = "https://en.wikipedia.org/wiki/Category:Mobile_phones_introduced_in_" + currentYear
        soup = self.soupFromUrl(wikiUrl)
        pageContent = self.getContent(soup, 'div', {'id':'mw-pages'})
        listItems = self.getAllContent(pageContent, 'li')
        for item in listItems:
            phoneName = item.text.lower()
            phoneName = self.fixString(phoneName)
            
            phoneList.append(phoneName)
            
        return phoneList
        

class PhoneScraperFactory:
    
    def createScraper(self, source, phone):
        if source == "TheVerge":
            return VergeScraper(phone)
        elif source == "Cnet":
            return CnetScraper(phone)
        elif source == "TechRadar":
            return TechRadarScraper(phone)
        else:
            raise ValueError("\'" + source + "\' is not a valid source. It may not be implemented.")
        
        


def errorHandling(e):
    print(e.args)
    print(traceback.format_exc())

def stringErrorHandling(errorString):
    print(errorString)

def scrapePhone(phone, source):
    try:
        scraper = PhoneScraperFactory().createScraper(source, phone)
    except ValueError as e:
        errorHandling(e)
        return []
    
    
    try:
        reviewSoup = scraper.getReview()
        scraper.scrape(reviewSoup)
    except Exception as e:
        errorHandling(e)
        return None, []
    
    
    jsonList = []
    
    
    if len(scraper.reviews) < 1:
        stringErrorHandling("no reviews found")
        return None, []
    else:
        for review in scraper.reviews:
            #review.printReview()
            jsonList.append(review.__dict__)
            
    phone = scraper.getPhoneInfo()    
    phoneJson = None
    
    if phone is not None:
        phoneJson = phone.__dict__
        
    return phoneJson, jsonList



def __main__(): 
    scraper = PhoneListScraper()
    
    year = datetime.datetime.now().year
    year = 2018
    
    
    phoneList = scraper.getPhones(year)
    print(phoneList)
    
    sources = ["Cnet", "TheVerge", "TechRadar"]
    
    dInteract = DatabaseInteract()
    
    for source in sources:
        for phone in phoneList:
            phoneObj, reviews = scrapePhone(phone, source)
            if len(reviews) > 0:
                dInteract.postReviews(reviews)
                dInteract.postPhoneInfo(phoneObj)
            
__main__()