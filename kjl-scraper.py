#!/usr/bin/env python3


import database
import dnbapi
from dnbRecord import DNBRecord
#import pandas as pd

def scrape():

    # create DB
    database.createDB()

    print("Scraping...")

    #query = 'tit=Klimawandel and location=onlinefree'    
    query = "sgt=K and jhr<2023 and jhr >2020 and spr=ger and mat=books sortBy idn/sort.descending"
    #query = "mat=books sortBy idn/sort.descending"


    records = dnbapi.dnb_sru(query, numberOfRecords=20)
    print(len(records), 'Ergebnisse')

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

    # database.displayBookContent()

if __name__ == '__main__':
    scrape()
