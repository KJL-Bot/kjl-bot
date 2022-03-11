
import unicodedata
from lxml import etree
import pytz
from datetime import datetime

class ISBN:

    def __init__(self, noDashes, withDashes, termsOfAvailability):
        self.noDashes = noDashes
        self.withDashes = withDashes
        self.termsOfAvailability = termsOfAvailability

    def __str__(self):
        return f"{self.noDashes} {self.withDashes} {self.termsOfAvailability}"
        

class DNBRecord:

    def __init__(self, xmlRecord):
        self.xmlRecord = xmlRecord
        self.parseXML()

    def parseXML(self):
        
        record = self.xmlRecord

        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
        
        # idn
        self.idn,_ = self.extractProperty(fieldType='controlfield', tagString='001', codeString='', xml=xml, ns=ns)

        # link to dataset
        self.linkToDataset = f"https://d-nb.info/{self.idn}"

        # ISBN
        self.isbns = self.extractISBNs(record, xml=xml, ns=ns)
   
        # last transaction
        self.lastDnbTransaction = self.extractLastTransaction(record, xml=xml, ns=ns)

        # projectedPublicationDate
        self.projectedPublicationDate = self.extractProjectedPublicationDate(record, xml=xml, ns=ns)

        # titel
        self.title,_ = self.extractProperty(fieldType='datafield', tagString='245', codeString='a', xml=xml, ns=ns)  

        # subTitle
        self.subTitle,_ = self.extractProperty(fieldType='datafield', tagString='245', codeString='b', xml=xml, ns=ns)

        # titleAuthor
        self.titleAuthor,_ = self.extractProperty(fieldType='datafield', tagString='245', codeString='c', xml=xml, ns=ns) 

        # authorName
        self.authorName,_ = self.extractProperty(fieldType='datafield', tagString='100', codeString='a', xml=xml, ns=ns)

        # authorDescription 100 a+b+c
        # self.authorDescription = self.extractPersonDetails(record, '100', xml=xml, ns=ns)

        # publication place
        self.publicationPlace,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='a', xml=xml, ns=ns)

        # publisher
        self.publisher,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='b', xml=xml, ns=ns)
    
        # publicationYear
        self.publicationYear,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='c', xml=xml, ns=ns)

        
    # fieldType can be 'controlfield' or 'datafield'
    def extractProperty(self, fieldType, tagString, codeString, xml, ns):

        # build path from tagNumber
        pathString = f"marc:{fieldType}[@tag = \'{tagString}\']"

        # add code if available
        if len(codeString) > 0:
            pathString += f"/marc:subfield[@code = \'{codeString}\']"
        
        propertyArray = xml.xpath(pathString, namespaces=ns)
        propertyTextArray = []

        for property in propertyArray:
            propertyTextArray.append(property.text)

        try:
            property = propertyArray[0].text
            #property = unicodedata.normalize("NFC", property)
        except:
            property = None #""
            if fieldType == "controlfield":
                property = "fail"

        # replace unwanted characters
        if property is not None:
            property = property.replace('\x98', '')
            property = property.replace('\x9c', '')

        return (property , propertyTextArray)



    def extractISBNs(self, record, xml, ns):

        #get relevant XML
        _, noDashesArray = self.extractProperty(fieldType='datafield', tagString='020', codeString='a', xml=xml, ns=ns)
        _, withDashesArray = self.extractProperty(fieldType='datafield', tagString='020', codeString='9', xml=xml, ns=ns)
        _, termsOfAvailabilityArray = self.extractProperty(fieldType='datafield', tagString='020', codeString='c', xml=xml, ns=ns)

        isbns = []

        for index, _ in enumerate(noDashesArray):
            
            # fill dictionary if data is available
            noDashes = noDashesArray[index] if len(noDashesArray) > index else ""
            withDashes = withDashesArray[index] if len(withDashesArray) > index else ""
            termsOfAvailability = termsOfAvailabilityArray[index] if len(termsOfAvailabilityArray) > index else ""

            # create ISBN
            isbn = ISBN(noDashes=noDashes, withDashes=withDashes, termsOfAvailability=termsOfAvailability)

            # add to output array
            isbns.append(isbn)

        return isbns

    # Returns last transaction as datetime
    def extractLastTransaction(self, record, xml, ns):

        # example: 20220102223003.0
        lastTransactionString,_ = self.extractProperty(fieldType='controlfield', tagString='005', codeString='', xml=xml, ns=ns)

        # localize to UTC
        lastTransaction = datetime.strptime(lastTransactionString, '%Y%m%d%H%M%S.%f')
        #timezone = pytz.utc # timezone('America/New_York')
        #lastTransactionWithTimeZone = timezone.localize(lastTransaction)

        # print(f"{lastTransactionString} -> {lastTransactionWithTimeZone}")

        return lastTransaction

    # Returns projected publicationMonth as datetime with the 1first of the month 00:00:00 UTC
    def extractProjectedPublicationDate(self, record, xml, ns):

        # example: 202112
        projectedPublicationDateString, _ = self.extractProperty(fieldType='datafield', tagString='263', codeString='a', xml=xml, ns=ns)

        # use try: except: but once, projectedPublicationDateString was '20 2.1'
        try:
            if projectedPublicationDateString is not None:

                # localize to UTC
                projectedPublicationDate = datetime.strptime(projectedPublicationDateString, '%Y%m')
                #timezone = pytz.utc
                #projectedPublicationDateWithTimeZone = timezone.localize(projectedPublicationDate)

                #print(f"{projectedPublicationDateString} -> {projectedPublicationDateWithTimeZone}")

                return projectedPublicationDate
        except:
            pass

        return None


    def extractPersonDetails(self, tagString, record, xml, ns):
        
        # author: 100

        # authorName 100 a
        authorName,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='a', xml=xml, ns=ns)

        # authorRelatorTerms 100 e
        authorRelatorTerm,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='e', xml=xml, ns=ns)

        # authorRelatorCodes 100 4
        authorRelatorCode,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='4', xml=xml, ns=ns)

        personString = f"{authorName} ({authorRelatorTerm})"