import sqlite3
from datetime import datetime, timedelta
import uuid
import rssFeed
import html

databaseName = "kjl.db"


#### General

def createDB():

    createBooksTable()
    createLogbook()

def executeCommand(command):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    # execute
    cursor.execute(command)
    connection.commit()

    # close
    connection.close()



######## Books

def createBooksTable():

    # Create books table
    command = """
    CREATE TABLE IF NOT EXISTS books (
        idn VARCHAR(10) PRIMARY KEY, 
        linkToDataset VARCHAR(128),
        
        isbnWithDashes VARCHAR(20), 
        isbnNoDashes VARCHAR(20), 
        isbnTermsOfAvailability VARCHAR(128), 

        addedToSql TIMESTAMP,
        updatedInSql TIMESTAMP,

        lastDnbTransaction TIMESTAMP,
        projectedPublicationDate TIMESTAMP,
        
        title VARCHAR(128),
        subTitle VARCHAR(128),
        titleAuthor VARCHAR(128),
        
        authorName VARCHAR(128),

        publicationPlace VARCHAR(128),
        publisher VARCHAR(128),
        publicationYear INT(4)

    );"""

    executeCommand(command)








def storeBook(book):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    addedToSql = datetime.utcnow()

    command = "INSERT INTO books (addedToSql, updatedInSql, \
            idn, linkToDataset, \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            lastDnbTransaction, projectedPublicationDate, \
            title, subTitle, titleAuthor, \
            authorName, \
            publicationPlace, publisher, publicationYear) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    newBookWasAdded = False
    isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
    isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
    isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None

    try:
        cursor.execute(command, \
            (addedToSql, addedToSql,\
            book.idn, book.linkToDataset,  \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            book.lastDnbTransaction, book.projectedPublicationDate, \
            book.title, book.subTitle, book.titleAuthor, \
            book.authorName, \
            book.publicationPlace, book.publisher, book.publicationYear)
            )

        print(f"Adding new book. Title: {book.title}")
        newBookWasAdded = True

    # ignore feedback on violation of UNIQUE contraint
    except sqlite3.IntegrityError:
        pass

    # other errors
    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        print("Error while inserting new book:")
        print(e)
        pass

    # close
    connection.commit()
    connection.close()

    return newBookWasAdded

def displayBookContent():

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    command = "SELECT idn, isbnWithDashes, DATETIME(addedToSql), DATETIME(lastDnbTransaction), DATE(projectedPublicationDate), publicationYear, authorName, title  FROM books ORDER BY idn DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    for book in books:
        print(book)
    

    connection.close()



########## Logbook
def createLogbook():
    # Create logbook
    command = """
    CREATE TABLE IF NOT EXISTS logbook (id CHAR(36) PRIMARY KEY, timestamp TIMESTAMP, description VARCHAR(128))
    """
    executeCommand(command)



def addUUIDsToLogbook():

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    command = "SELECT timestamp FROM logbook WHERE id IS NULL ORDER BY timestamp"
    cursor.execute(command)
    lbEntries = cursor.fetchall()

    for lbEntry in lbEntries:
        timestamp = lbEntry[0]
        newUUID = str(uuid.uuid4())
        command = "UPDATE logbook SET id = ? WHERE timestamp = ?"
        print(f"{timestamp} {newUUID} {command}")
        
        try:
            cursor.execute(command, (newUUID, timestamp))
        except Exception as e:
         print(e)

    # close
    connection.commit()
    connection.close()


def logMessage(logMessage):
    
    utctime = datetime.utcnow()
    newUUID = str(uuid.uuid4())

    #timezone = pytz.utc
    #utctime = timezone.localiz(utctime)

    command = "INSERT INTO logbook (timestamp, id, description) VALUES (?, ?, ?)"

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    try:
        cursor.execute(command, (utctime, newUUID, logMessage))
    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()

def generateRSSEntries():

    # result are stored here
    rssEntries = []

    # connect    
    connection = sqlite3.connect(databaseName, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()   

    # get logbook entries
    command = "SELECT timestamp, id, description  FROM logbook ORDER BY timestamp DESC"
    cursor.execute(command)
    logbookEntries = cursor.fetchall()

    # go through each entry
    for logbookEntry in logbookEntries:

        (logBookTimestamp, logBookId, logBookDescription) = logbookEntry

        thirtySecondsEarlier = logBookTimestamp - timedelta(seconds = 30)
        thirtySecondsLater = logBookTimestamp + timedelta(seconds = 30)

        # get related books
        command = "SELECT idn, isbnWithDashes, title, subTitle, titleAuthor, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset FROM books WHERE addedToSql BETWEEN ? AND ? ORDER BY idn DESC"


        try:
            cursor.execute(command, (thirtySecondsEarlier, thirtySecondsLater))
            books = cursor.fetchall()

            # start des Eintrags
            numberOfBooks = len(books)
            entryLines = [f"Die folgenden {numberOfBooks} Bücher wurden zur DNB hinzugefügt.", ""]
            if numberOfBooks == 1:
                entryLines = [f"Das folgende Buch wurde zur DNB hinzugefügt.", ""]

            for (idn, isbnWithDashes, title, subTitle, titleAuthor, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset) in books:
                
                entryLines.append(f"<b>{title}</b>")
                
                if subTitle is not None:
                    entryLines.append(f"<i>{subTitle}</i>")  

                if titleAuthor is not None:
                    entryLines.append(f"Von {titleAuthor}")
                
                entryLines.append(f"{publicationPlace}, {publicationYear}")
                
                if projectedPublicationDate is not None:
                    entryLines.append(f"Erwartete Publikation laut DNB: {projectedPublicationDate.strftime('%Y-%m')}")
                
                entryLines.append(f"DNB Link: <a href=\"{linkToDataset}\">{linkToDataset}</a>")
                entryLines.append(f"IDN: {idn}")

                if isbnWithDashes is not None:
                    entryLines.append(f"ISBN: {isbnWithDashes}")
                
                entryLines.append(f"")

            # Convert lines into string
            rssContent = '<br>\n'.join(entryLines)

            # create new entry
            entryTitle = f"{numberOfBooks} neue Bücher in DNB Datenbank"
            if numberOfBooks == 1:
                entryTitle = f"Ein neues Buch in DNB Datenbank"   

            rssEntry = rssFeed.rssEntry(id = logBookId, publicationDate = logBookTimestamp, title = entryTitle, content = rssContent)
            rssEntries.append(rssEntry)

        except Exception as e:
            print(f"Fehler beim suchen der Bücher für logbook Entry mit id {logBookId}.")
            print(e)


    connection.close()

    return rssEntries