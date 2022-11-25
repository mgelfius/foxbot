from datetime import date, datetime, timedelta
import random
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import subprocess
import fileinput, sys
import re

baseUrl = "https://www.gocomics.com/foxtrot/"
dailyRunStart = date(1988, 4, 11)
dailyRunEnd = date(2006, 12, 31)
modernRunStart = date(2009, 11, 15)
currentDate = date.today().strftime("%Y/%m/%d")

def main():
    dayOfWeek = datetime.now().weekday()

    todaysUrl = ""
    randomUrl = ""

    if dayOfWeek == 6:
        todaysUrl = tryToDownloadGoComics(baseUrl + currentDate, "foxtrotToday")
    else:
        todaysUrl = tryToGetStrip("foxtrotToday", modernRunStart, date.today())

    randomUrl = tryToGetStrip("foxtrotRandom", dailyRunStart, dailyRunEnd)

    prepareTweet(randomUrl, "Classic", "foxtrotRandom")
    prepareTweet(todaysUrl, "Modern", "foxtrotToday")

def tryToGetStrip(randomOrToday, startDate, endDate):
    retryGeneration = ""
    while retryGeneration == "":
        retryUrl = baseUrl + generateRandomDate(startDate, endDate)
        retryGeneration = tryToDownloadGoComics(retryUrl, randomOrToday)
    return retryGeneration

def tryToDownloadGoComics(randomUrl, randomOrToday):
    try:
        randomStripImgLink = getGoComicsStrip(randomUrl)
        downloadStrip(randomStripImgLink, randomOrToday)
        return randomUrl
    except Exception as e:
        print(e)
        return ""

def tryToDownload(randomUrl):
    try:
        randomLink = getStripLink(randomUrl)
        randomStripImgLink = getStrip(randomLink)
        downloadStrip(randomStripImgLink, "foxtrotRandom")
        return randomLink
    except Exception as e:
        print(e)
        return ""

def generateRandomDate(runStart, runEnd):
    random.seed(a = None)
    totalDays = (runEnd - runStart).days
    randomDay = random.randrange(totalDays)
    return (runStart + timedelta(days=randomDay)).strftime("%Y/%m/%d")

def generateRandomSunday(runStart, runEnd, currentDate):
    randomDate = date(1970, 1, 1)
    random.seed(a = None)
    while randomDate.weekday() != 6 and randomDate.strftime("%Y/%m/%d") != currentDate:
        totalDays = (runEnd - runStart).days
        randomDay = random.randrange(totalDays)
        randomDate = runStart + timedelta(days=randomDay)

    return randomDate.strftime("%Y/%m/%d")

def getStripLink(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    return soup.find("figure").a.get('href')

def getStrip(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    return soup.find("figure").img.get("src")

def getGoComicsStrip(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
        }
    req = Request(url, headers=headers)
    webpage = requests.get(url, headers).content
    soup = BeautifulSoup(webpage, 'html.parser')
    return soup.find(class_="item-comic-image").img.get("src")

def downloadStrip(link, stripName):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
        }
    r = requests.get(link, stream=True, headers=headers)
    r.raw.decode_content = True
    with open('./FoxtrotImg/' + stripName + '.png', 'wb') as handler:
        handler.write(r.content)

def uploadMedia(randomOrToday):
    for line in fileinput.input([r".\uploadmedia.bat"], inplace=True):
        line = re.sub("replaceWithImageName", randomOrToday, line)
        sys.stdout.write(line)

    responseValue = subprocess.check_output([r'.\uploadmedia.bat'])

    for line in fileinput.input([r".\uploadmedia.bat"], inplace=True):
        line = re.sub(randomOrToday, "replaceWithImageName", line)
        sys.stdout.write(line)
    
    return responseValue

def sendTweet(payload, mediaId):
    for line in fileinput.input([r".\sendTweet.bat"], inplace=True):
        line = re.sub("replaceWithStatus", payload, line)
        line = re.sub("replaceWithMediaId", mediaId, line)
        sys.stdout.write(line)

    responseValue = subprocess.check_output([r'.\sendTweet.bat'])

    for line in fileinput.input([r".\sendTweet.bat"], inplace=True):
        line = re.sub(payload, "replaceWithStatus", line)
        line = re.sub(mediaId, "replaceWithMediaId", line)
        sys.stdout.write(line)

    print(responseValue)

def prepareTweet(link, modernOrClassic, randomOrToday):
    payload = modernOrClassic + " Foxtrot for " + currentDate + ". " + link
    mediaId = str(uploadMedia(randomOrToday))
    index = mediaId.find('media_id_string')
    mediaIdFinal = mediaId[(index + 18):(index + 18 + 19)]
    sendTweet(payload, mediaIdFinal)

if __name__ == "__main__":
    main()