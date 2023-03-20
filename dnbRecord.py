
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

        # secondary authorName
        self.secondaryAuthorName,_ = self.extractProperty(fieldType='datafield', tagString='700', codeString='a', xml=xml, ns=ns)

        # sortingAuthor
        self.sortingAuthor = self.extractSortingAuthor(record=record, xml=xml, ns=ns)

        # authorDescription 100 a+b+c
        # self.authorDescription = self.extractPersonDetails(record, '100', xml=xml, ns=ns)

        # publication place
        self.publicationPlace,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='a', xml=xml, ns=ns)

        # publisher
        self.publisher,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='b', xml=xml, ns=ns)

        # publicationYear
        self.publicationYear,_ = self.extractProperty(fieldType='datafield', tagString='264', codeString='c', xml=xml, ns=ns)

        # keywords650 - Subject Added Entry - Topical Term
        _, self.keywords = self.extractProperty(fieldType='datafield', tagString='650', codeString='a', xml=xml, ns=ns)
        self.keywords = self.eleminateTerms(self.keywords, '(') # remove terms starting with open bracket

        # keywords653 -  Index Term - Uncontrolled
        _, self.keywords653 = self.extractProperty(fieldType='datafield', tagString='653', codeString='a', xml=xml, ns=ns)
        self.keywords653 = self.eleminateTerms(self.keywords653, '(') # remove terms starting with open bracket

        # genre655_0,a,2 -  Index Term-Genre/Form
        self.genre655_0,_ = self.extractProperty(fieldType='datafield', tagString='655', codeString='0', xml=xml, ns=ns)
        self.genre655_a,_ = self.extractProperty(fieldType='datafield', tagString='655', codeString='a', xml=xml, ns=ns)
        self.genre655_2,_ = self.extractProperty(fieldType='datafield', tagString='655', codeString='2', xml=xml, ns=ns)

    # returns all elements from incoming list if they do not start with <firstCharacter>
    def eleminateTerms(self, termsArray, firstCharacter):
        newArray = []
        for term in termsArray:
            if not term.startswith(firstCharacter):
                newArray.append(term)
        return newArray


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

    # combines names with roles 'aut' in datafields 100 and 700 and returns the first of the names
    def extractSortingAuthor(self, record, xml, ns):

        # all names from dataField 100
        _, names100 = self.extractProperty(fieldType='datafield', tagString='100', codeString='a', xml=xml, ns=ns)

        # all relatorCodes from dataField 100
        _, relatorCodes100 = self.extractProperty(fieldType='datafield', tagString='100', codeString='4', xml=xml, ns=ns)

        # all names from dataField 700
        _, names700 = self.extractProperty(fieldType='datafield', tagString='700', codeString='a', xml=xml, ns=ns)

        # all relatorCodes from dataField 700
        _, relatorCodes700 = self.extractProperty(fieldType='datafield', tagString='700', codeString='4', xml=xml, ns=ns)

        # reduce names to relatorCode = 'aut' -> only use authors
        authorNames100 = self.reduceNamesToCode(names100, relatorCodes100, 'aut') # main author
        authorNames700 = self.reduceNamesToCode(names700, relatorCodes700, 'aut') # secondary author

        allNames100 = self.reduceNamesToCode(names100, relatorCodes100, None)
        allNames700 = self.reduceNamesToCode(names700, relatorCodes700, None)

        # make one list out of three
        allAuthorNames = authorNames100
        allAuthorNames.extend(authorNames700)

        # if we did not find any author, extend the list by all the other names
        if len(allAuthorNames) == 0:
            allAuthorNames.extend(allNames100)
            allAuthorNames.extend(allNames700)

        # the first entry is the autor we want to return
        sortingAuthor = None # default
        if len(allAuthorNames) > 0:
            sortingAuthor = allAuthorNames[0].strip()

        return sortingAuthor

    # goes through array of <codes>, finds the codes matching <wantedCode> and filters <names> accrding to the matching INDEX
    # returns filtered <names>
    def reduceNamesToCode(self, names, codes, wantedCode):

        # result goes here
        reducedNames = []

        # go throug hall codes
        for index, code in enumerate(codes):

            # did we find the code we wanted? Or do we want all names (-> wantedCode is None)?
            if (code == wantedCode) or (wantedCode is None):

                # can we match a name?
                if len(names) > index:

                    # then grab name and add to results
                    name = names[index]
                    reducedNames.append(name)

        return reducedNames


    def extractPersonDetails(self, tagString, record, xml, ns):

        # author: 100

        # authorName 100 a
        authorName,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='a', xml=xml, ns=ns)

        # authorRelatorTerms 100 e
        authorRelatorTerm,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='e', xml=xml, ns=ns)

        # authorRelatorCodes 100 4
        authorRelatorCode,_ = self.extractProperty(fieldType='datafield', tagString=tagString, codeString='4', xml=xml, ns=ns)

        personString = f"{authorName} ({authorRelatorTerm})"


    #def extractKeywords(self, record, xml, ns):

        # SUBJECT ADDED ENTRY--TOPICAL TERM: MARC=650, codeString = a
        # there can be several entries of type MARC 650

        # authorName 100 a
        #_,keywords = self.extractProperty(fieldType='datafield', tagString='650', codeString='a', xml=xml, ns=ns)

        #return keywords
