#!/usr/bin/env python3


import database
import dnbapi
from dnbRecord import DNBRecord
import pandas as pd

def scrape():

    # create DB
    database.createDB()

    print("Scraping...")

    #query = 'tit=Klimawandel and location=onlinefree'    
    query = "sgt=K and jhr<2023 and jhr >2020 and spr=ger and mat=books sortBy idn/sort.descending"
    #query = "mat=books sortBy idn/sort.descending"


    records = dnbapi.dnb_sru(query, numberOfRecords=10)
    print(len(records), 'Ergebnisse')

    # convert to array of dicts
    books = []
    for record in records:
        book = DNBRecord(xmlRecord = record)
        books.append(book)

    # store in db
    for book in books: 
        database.storeBook(book)

    # convert to pandas table
    #df = pd.DataFrame(books)
    #print(df)

    database.displayBookContent()

if __name__ == '__main__':
    scrape()