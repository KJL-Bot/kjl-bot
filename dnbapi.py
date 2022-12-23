import requests
from bs4 import BeautifulSoup as soup
import unicodedata
from lxml import etree
import time
import datetime

# creates query of the given year and the given number of records
def createQuery(year, numberOfRecords):

    dnbSearchQuery = f"sgt=K and jhr>={year} and jhr<={year} and spr=ger and mat=books sortBy idn/sort.descending"

    return dnbSearchQuery

def dnb_sru(query, numberOfRecords=100, returnFirstRecordsOnly = False):

    base_url = "https://services.dnb.de/sru/dnb"

    params = {'recordSchema' : 'MARC21-xml',
          'operation': 'searchRetrieve',
          'version': '1.1',
          'maximumRecords': str(numberOfRecords),
          'query': query
         }

    r = requests.get(base_url, params=params)
    print(r.url)
    xml = soup(r.content, features="lxml")
    records = xml.find_all('record', {'type':'Bibliographic'})

    # early exit
    if returnFirstRecordsOnly:
        return records

    if len(records) < 100:
        return records

    else:

        num_results = 100
        i = 101
        while num_results == 100 and len(records) < numberOfRecords:

            params.update({'startRecord': i})
            r = requests.get(base_url, params=params)
            print(r.url)
            xml = soup(r.content, features="lxml")
            new_records = xml.find_all('record', {'type':'Bibliographic'})
            records+=new_records
            i+=100
            num_results = len(new_records)

            # sleep 1 sec
            time.sleep(1)


        return records
