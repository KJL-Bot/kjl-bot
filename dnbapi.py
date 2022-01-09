import requests
from bs4 import BeautifulSoup as soup
import unicodedata
from lxml import etree

def dnb_sru(query, numberOfRecords=100, returnFirstRecordsOnly = True):
    
    base_url = "https://services.dnb.de/sru/dnb"
    
    params = {'recordSchema' : 'MARC21-xml',
          'operation': 'searchRetrieve',
          'version': '1.1',
          'maximumRecords': str(numberOfRecords),
          'query': query
         }
    
    r = requests.get(base_url, params=params)
    #print(r.url)
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
        while num_results == 100:
            
            params.update({'startRecord': i})
            r = requests.get(base_url, params=params)
            xml = soup(r.content, features="lxml")
            new_records = xml.find_all('record', {'type':'Bibliographic'})
            records+=new_records
            i+=100
            num_results = len(new_records)
            
        return records
