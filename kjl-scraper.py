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

    # insert here. get year to scrape
    nextScrapeYear = logbookManager.determineNextScrapeYear(numberOfYearsToScrape = config.numberOfYearsToScrape)

    # create query
    dnbSearchQuery = dnbapi.createQuery(year=nextScrapeYear)


    # log scrape start
    logbookMessageId = logbookManager.logScrapeStart(year=nextScrapeYear)

    # get records from DNB
    #records = dnbapi.dnb_sru(dnbSearchQuery, numberOfRecords=config.numberOfRetrievedRecords)
    records = dnbapi.dnb_sru(dnbSearchQuery, numberOfRecords=50)
    #print(len(records), 'Ergebnisse')

    # log number of retrieved records
    logbookManager.logRecordRetrieval(numberOfRecords=len(records))
    #logbookManager.logMessage(relatesToIDN=None, description=f"Retrieved {len(records)} DNB records")

    # convert to array of books
    books = []
    for record in records:
        book = DNBRecord(xmlRecord = record)
        books.append(book)

    # store in db and associate each book with the logbookMessageId
    insertedBookCounter = 0
    updatedCounter = 0
    for book in books:
        status = bookManager.insertOrUpdateBook(book, logbookMessageId)
        if status == "inserted":
            insertedBookCounter += 1

        if status == "updated":
            updatedCounter += 1

    # log
    if insertedBookCounter > 0:
        #logbookManager.logMessage(relatesToIDN=None, description=f"Added {insertedBookCounter} books to database")
        logbookManager.logBooksAddition(numberOfBooks=insertedBookCounter)

    if updatedCounter > 0:
        #logbookManager.logMessage(relatesToIDN=None, description=f"Updated {updatedCounter} books in database")
        logbookManager.logBooksUpdate(numberOfBooks=updatedCounter)

    # match all DB entries against relevant publishers
    publishers.matchBooksToPublishers()
    #logbookManager.logMessage("Matched to publishers")

    # identify all the books that are relevant for playout
    bookManager.identifyRelevantBooks()
    #logbookManager.logMessage("Updated book relevancies")

    # create rss entries
    rssEntries = rssManager.generateRSSEntries()
    #logbookManager.logMessage("Created RSS entries")

    # generate and store RSS feed locally
    rssFilePath = rssManager.generateFeed(rssEntries)
    #logbookManager.logMessage("Generated RSS Feed")

    # transfer xml file to FTP server
    ftpCoordinator.transferFileViaFTP(rssFilePath, config.ftpTargetFolder) # artistic engines
    #logbookManager.logMessage("Transferred RSS to Artistic Engines FTP server")
    #print(f"Feed URL is: {config.rssFeedUrl}")

    # create JSON file recent valid books
    validBookEntries = jsonExporter.generateValidBookEntries(config.maximumNumberOfJSONEntries)
    jsonFilePath = jsonExporter.writeBookEntriesToJSONFile(validBookEntries)
    #logbookManager.logMessage("Generated JSON Feed")

    # transfer JSON file to Artistic Engines FTP server
    ftpCoordinator.transferFileViaFTP(jsonFilePath, config.ftpTargetFolder)
    #logbookManager.logMessage("Transferred JSON to Artistic Engines FTP server")
    #print(f"JSON URL is: {config.jsonFeedUrl}")

    # transfer JSON file to KJL FTP server
    ftpCoordinator.transferFileViaFTP_SSL(jsonFilePath, config.kjlFtpSSLTargetDir) # KJL Bot Server
    logbookManager.logMessage(relatesToIDN=None, description="Transferred JSON to KJL FTP server")


    # bookManager.displayBookContent()

if __name__ == '__main__':
    #bookManager.identifyRelevantBooks()
    scrape()
