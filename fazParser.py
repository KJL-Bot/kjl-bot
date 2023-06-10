#!/usr/bin/env python3

import feedparser
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import reviewManager
from datetime import datetime
import string


def parseFeed():

    reviewSite = "FAZ"
    rssFeed = "https://www.faz.net/rss/aktuell/feuilleton/buecher/rezensionen/kinderbuch/"

    d = feedparser.parse(rssFeed)

    # count how many reviews were retrieved
    reviewCounter = 0

    for n in range(0,len(d.entries)):

        title = d.entries[n].title
        pageUrl = d.entries[n].link
        description = d.entries[n].description

        # print (title) # code 1
        # print (pageUrl) # code 2
        # print (description) # code 3
        # print()

        (published, author, title) = extractBookDetails(pageUrl)

        # print(f"Storing Review: {published} -> {author}: {title}")

        reviewManager.addReview(
                published = published,
                scraper = "fazScraper",
                reviewSite = "FAZ",
                author = author,
                title = title,
                isbnWithDashes = None,
                url=pageUrl
        )

        # count
        reviewCounter += 1

    return reviewCounter

def extractBookDetails(pageUrl):

    page = urlopen(pageUrl)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # get author and title
    paragraphs = soup.find_all("p", class_="atc-TextParagraph")
    author = None
    title = None

    for paragraph in paragraphs:
        strongTag = paragraph.strong
        if strongTag is not None:
            strongText = strongTag.get_text()
            #print(strongText)

            # format: author(s): title
            match = re.search("(.+): (.+)", strongText)

            # author
            author = match.group(1)

            # replace 'und' with ','
            #author = author.replace(" und", ',')

            # title
            title = match.group(2)

            # remove quotes
            title = title.replace('„', '')
            title = title.replace('“', '')

            # strip punctuation
            title = title.strip(string.punctuation)

            #print(f"Author: {author}")
            #print(f"Title: {title}")

    # published
    timeParagraph = soup.find("time")
    publishedString = timeParagraph["datetime"]
    publishedStringWithCorrectTimeZomeFormat = publishedString[:-5] # remove timezone
    published = datetime.fromisoformat(publishedStringWithCorrectTimeZomeFormat)

    # return results
    return (published, author, title)


if __name__ == '__main__':
    numberOfRetrievedReviews = parseFeed()
    print(f"Retrieved {numberOfRetrievedReviews} FAZ reviews")
