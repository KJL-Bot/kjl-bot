#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as soup
import unicodedata
from lxml import etree
import pandas as pd

def dnb_sru(query, numberOfRecords=100, returnFirstRecordsOnly = True):
    
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
        while num_results == 100:
            
            params.update({'startRecord': i})
            r = requests.get(base_url, params=params)
            xml = soup(r.content, features="lxml")
            new_records = xml.find_all('record', {'type':'Bibliographic'})
            records+=new_records
            i+=100
            num_results = len(new_records)
            
        return records

# fieldType can be 'controlfield' or 'datafield'
def extractProperty(fieldType, tagString, codeString, xml, ns):

    # build path from tagNumber
    pathString = f"marc:{fieldType}[@tag = \'{tagString}\']"

    # add code if available
    if len(codeString) > 0:
        pathString += f"/marc:subfield[@code = \'{codeString}\']"
    
    propertyArray = xml.xpath(pathString, namespaces=ns)
    
    try:
        property = propertyArray[0].text
        #property = unicodedata.normalize("NFC", titel)
    except:
        property = ""
        if fieldType == "controlfield":
            property = "fail"

    return property

def parse_record(record):
    
    ns = {"marc":"http://www.loc.gov/MARC21/slim"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    #idn
    idn = extractProperty(fieldType='controlfield', tagString='001', codeString='', xml=xml, ns=ns)

    # last transaction
    lastTransaction = extractProperty(fieldType='controlfield', tagString='005', codeString='', xml=xml, ns=ns)  

    # titel
    title = extractProperty(fieldType='datafield', tagString='245', codeString='a', xml=xml, ns=ns)

    # subTitle
    subTitle = extractProperty(fieldType='datafield', tagString='245', codeString='b', xml=xml, ns=ns)

    # author
    author = extractProperty(fieldType='datafield', tagString='245', codeString='c', xml=xml, ns=ns)

    # ISBN
    isbn = extractProperty(fieldType='datafield', tagString='020', codeString='9', xml=xml, ns=ns)

    # publication place
    publicationPlace = extractProperty(fieldType='datafield', tagString='264', codeString='a', xml=xml, ns=ns)

    # publisher
    publisher = extractProperty(fieldType='datafield', tagString='264', codeString='b', xml=xml, ns=ns)
 
    # publicationYear
    publicationYear = extractProperty(fieldType='datafield', tagString='264', codeString='c', xml=xml, ns=ns)

    # projectedPublicationDate
    projectedPublicationDate = extractProperty(fieldType='datafield', tagString='263', codeString='a', xml=xml, ns=ns)
 
    # assemble results
    meta_dict = {"idn": idn,
                "isbn": isbn,
                "title": title,
                "subTitle": subTitle,
                "author": author,
                "publicationPlace": publicationPlace,
                "publisher": publisher,
                "publicationYear": publicationYear,
                "projectedPublicationDate": projectedPublicationDate,
                "lastTransaction": lastTransaction}


    
    return meta_dict

def scrape():
    print("Scraping...")

    #query = 'tit=Klimawandel and location=onlinefree'    
    query = "sgt=K and jhr<2022 and jhr >2020 and spr=ger and mat=books sortBy idn/sort.descending"
    #query = "mat=books sortBy idn/sort.descending"


    records = dnb_sru(query, numberOfRecords=20)
    print(len(records), 'Ergebnisse')

    output = [parse_record(record) for record in records]
    df = pd.DataFrame(output)
    print(df)

if __name__ == '__main__':
    scrape()