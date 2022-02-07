#!/usr/bin/env python3


import database
import dnbapi
from dnbRecord import DNBRecord
import rssFeed
import config
import ftpCoordinator

def scrape():


    # create DB
    database.createDB()

    print("Scraping...")

 
    dnbSearchQuery = config.dnbSearchQuery

    records = dnbapi.dnb_sru(dnbSearchQuery, numberOfRecords=50)
    #print(len(records), 'Ergebnisse')

    # convert to array of dicts
    books = []
    for record in records:
        book = DNBRecord(xmlRecord = record)
        books.append(book)

    # store in db
    newBookCounter = 0
    for book in books: 
        newBookWasAdded = database.storeBook(book)
        if newBookWasAdded:
            newBookCounter += 1

    # log activity
    if newBookCounter > 0:
        logMessage = f"Scraped DNB. Added {newBookCounter} new books."
        database.logMessage(logMessage)


    # create rss entries
    print("Creating RSS entries.")
    rssEntries = database.generateRSSEntries()

    # generate and store RSS feed locally
    print("Generating RSS Feed.")
    rssFilePath = rssFeed.generateFeed(rssEntries)

    # transfer xml file to FTP server
    print("Transfering to FTP server.")
    ftpCoordinator.transferFile(rssFilePath, config.ftpTargetFolder)
    print(f"Feed URL is: {config.rssFeedUrl}")

    # database.displayBookContent()

if __name__ == '__main__':
    scrape()
