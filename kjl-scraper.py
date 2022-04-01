#!/usr/bin/env python3

import config
import mariaDatabase
import bookManager
import logbookManager
import dnbapi
from dnbRecord import DNBRecord
import rssManager
import ftpCoordinator
import publishers

def scrape():


    # create tables
    bookManager.createBooksTable()
    logbookManager.createLogbook()


    print("Scraping...")

    dnbSearchQuery = config.dnbSearchQuery

    records = dnbapi.dnb_sru(dnbSearchQuery, numberOfRecords=config.numberOfRetrievedRecords)
    #print(len(records), 'Ergebnisse')

    # convert to array of dicts
    books = []
    for record in records:
        book = DNBRecord(xmlRecord = record)
        books.append(book)

    # store in db
    newBookCounter = 0
    for book in books: 
        newBookWasAdded = bookManager.storeBook(book)
        if newBookWasAdded:
            newBookCounter += 1

    # match all DB entries against relevant publishers
    print("Matching to publishers...")
    publishers.matchBooksToPublishers()

    # log activity
    if newBookCounter > 0:
        logMessage = f"Scraped DNB. Added {newBookCounter} new books."
        logbookManager.logMessage(logMessage)


    # create rss entries
    print("Creating RSS entries.")
    rssEntries = rssManager.generateRSSEntries()

    # generate and store RSS feed locally
    print("Generating RSS Feed.")
    rssFilePath = rssManager.generateFeed(rssEntries)

    # transfer xml file to FTP server
    print("Transfering to FTP server.")
    ftpCoordinator.transferFile(rssFilePath, config.ftpTargetFolder)
    print(f"Feed URL is: {config.rssFeedUrl}")

    # bookManager.displayBookContent()

if __name__ == '__main__':
    scrape()
