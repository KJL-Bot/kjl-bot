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
import jsonExporter

def scrape():


    # create tables
    bookManager.createBooksTable()
    logbookManager.createLogbook()

    # scrape DNB
    print("Scraping...")

    dnbSearchQuery = config.dnbSearchQuery
    records = dnbapi.dnb_sru(dnbSearchQuery, numberOfRecords=config.numberOfRetrievedRecords)
    #print(len(records), 'Ergebnisse')

    # convert to array of books
    books = []
    for record in records:
        book = DNBRecord(xmlRecord = record)
        books.append(book)

    # prepare lookbook by creating an initial entry (to be updated later)
    logbookMessageId = logbookManager.createInitialLogbookMessage()

    # store in db and associate each book with the logbookMessageId
    newBookCounter = 0
    for book in books:
        newBookWasAdded = bookManager.storeBook(book, logbookMessageId)
        if newBookWasAdded:
            newBookCounter += 1

            # log keywords if there are any
            if len(book.keywords) > 0:
                message = f"Keywords for book detected: {book.linkToDataset} -> {book.keywords}"
                logbookManager.logMessage(message)

    # match all DB entries against relevant publishers
    print("Matching to publishers...")
    publishers.matchBooksToPublishers()

    # log activity using previously create logbookMessageId
    if newBookCounter > 0:
        logMessage = f"Added {newBookCounter} new book(s)."
    else:
        logMessage = f"Scraped DNB with no new results."

    #logbookManager.logMessage(logMessage)
    logbookManager.updateLogbookMessageWithId(logbookMessageId, logMessage)

    # create rss entries
    print("Creating RSS entries.")
    rssEntries = rssManager.generateRSSEntries()

    # generate and store RSS feed locally
    print("Generating RSS Feed.")
    rssFilePath = rssManager.generateFeed(rssEntries)

    # transfer xml file to FTP server
    print("Transfering RSS to FTP server.")
    ftpCoordinator.transferFileViaFTP(rssFilePath, config.ftpTargetFolder) # artistic engines
    print(f"Feed URL is: {config.rssFeedUrl}")

    # create JSON file recent valid books
    print("Generating JSON Feed.")
    validBookEntries = jsonExporter.generateValidBookEntries(20000)
    jsonFilePath = jsonExporter.writeBookEntriesToJSONFile(validBookEntries)

    # transfer JSON file to Artistic Engines FTP server
    print("Transfering JSON to Artistic Engines FTP server.")
    ftpCoordinator.transferFileViaFTP(jsonFilePath, config.ftpTargetFolder)
    print(f"JSON URL is: {config.jsonFeedUrl}")

    # transfer JSON file to KJL FTP server
    print("Transfering JSON to KJL FTP server.")
    ftpCoordinator.transferFileViaFTP_SSL(jsonFilePath, config.kjlFtpSSLTargetDir) # KJL Bot Server    



    # bookManager.displayBookContent()

if __name__ == '__main__':
    scrape()
