from datetime import date, datetime, timedelta
import random
import requests
from bs4 import BeautifulSoup
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

    # If it's Sunday, get the new strip
    # If there isn't a new strip, get a random modern strip
    if dayOfWeek == 6:
        todaysUrl = tryToDownloadGoComics(baseUrl + currentDate, "foxtrotToday")
        if todaysUrl == "":
            todaysUrl = tryToGetStrip("foxtrotToday", modernRunStart, date.today())
    else:
        todaysUrl = tryToGetStrip("foxtrotToday", modernRunStart, date.today())

    randomUrl = tryToGetStrip("foxtrotRandom", dailyRunStart, dailyRunEnd)

    prepareTweet(randomUrl, "Classic", "foxtrotRandom")
    prepareTweet(todaysUrl, "Modern", "foxtrotToday")

# If the strip doesn't exist for that day, regenerate date and try again
def tryToGetStrip(randomOrToday, startDate, endDate):
    retryGeneration = ""
    while retryGeneration == "":
        retryUrl = baseUrl + generateRandomDate(startDate, endDate)
        retryGeneration = tryToDownloadGoComics(retryUrl, randomOrToday)
    return retryGeneration

# Try to download the strip and return a link. 
# If unsuccessful, return an empty string
def tryToDownloadGoComics(randomUrl, randomOrToday):
    try:
        randomStripImgLink = getGoComicsStrip(randomUrl)
        downloadStrip(randomStripImgLink, randomOrToday)
        return randomUrl
    except Exception as e:
        print(e)
        return ""

# Generate a random date within a range formatted for the GoComics url
def generateRandomDate(runStart, runEnd):
    random.seed(a = None)
    totalDays = (runEnd - runStart).days
    randomDay = random.randrange(totalDays)
    return (runStart + timedelta(days=randomDay)).strftime("%Y/%m/%d")

# Find the strip on the page, and return the image link
def getGoComicsStrip(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
        }
    webpage = requests.get(url, headers).content
    soup = BeautifulSoup(webpage, 'html.parser')
    return soup.find(class_="item-comic-image").img.get("src")

# Download the image to ./FoxtrotImg as either foxtrotToday or foxtrotRandom
def downloadStrip(link, stripName):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
        }
    r = requests.get(link, stream=True, headers=headers)
    r.raw.decode_content = True
    with open('./FoxtrotImg/' + stripName + '.png', 'wb') as handler:
        handler.write(r.content)

# Uploads the image to twitter, returning the response.
# Rewrites the batch file with the image name before execution
# and writes it back before returning the output.
def uploadMedia(randomOrToday):
    for line in fileinput.input([r".\uploadmedia.bat"], inplace=True):
        line = re.sub("replaceWithImageName", randomOrToday, line)
        sys.stdout.write(line)

    responseValue = subprocess.check_output([r'.\uploadmedia.bat'])

    for line in fileinput.input([r".\uploadmedia.bat"], inplace=True):
        line = re.sub(randomOrToday, "replaceWithImageName", line)
        sys.stdout.write(line)
    
    return responseValue

# Sends the tweet.
# Rewrites the batch file with the media ID and 
# tweet status before execution and writes it back.
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

# Builds the tweet status, uploads the image, and finds the media ID
# before sending the tweet.
def prepareTweet(link, modernOrClassic, randomOrToday):
    payload = modernOrClassic + " Foxtrot for " + date.today().strftime("%m/%d/%Y") + ". " + link
    mediaId = str(uploadMedia(randomOrToday))
    index = mediaId.find('media_id_string')
    mediaIdFinal = mediaId[(index + 18):(index + 37)]
    sendTweet(payload, mediaIdFinal)

if __name__ == "__main__":
    main()