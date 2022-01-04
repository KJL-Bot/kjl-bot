import sqlite3
from datetime import datetime

databaseName = "/home/pi/developer/kjl/kjl-bot/kjl.db"

def createDB():

    createBooksTable()
    createLogbook()

def createBooksTable():

    # Create books table
    command = """
    CREATE TABLE IF NOT EXISTS books (
        idn VARCHAR(10) PRIMARY KEY, 
        linkToDataset VARCHAR(128),
        
        isbnWithDashes VARCHAR(20), 
        isbnNoDashes VARCHAR(20), 
        isbnTermsOfAvailability VARCHAR(128), 

        addedToSql DATE,

        lastDnbTransaction DATE,
        projectedPublicationDate DATE,
        
        title VARCHAR(128),
        subTitle VARCHAR(128),
        titleAuthor VARCHAR(128),
        
        authorName VARCHAR(128),

        publicationPlace VARCHAR(128),
        publisher VARCHAR(128),
        publicationYear INT(4)

    );"""

    executeCommand(command)

def createLogbook():
    # Create logbook
    command = """
    CREATE TABLE IF NOT EXISTS logbook (timestamp DATE PRIMARY KEY, description VARCHAR(128))
    """
    executeCommand(command)


def logMessage(logMessage):

    utctime = datetime.utcnow()
    #timezone = pytz.utc
    #utctime = timezone.localiz(utctime)

    command = "INSERT INTO logbook (timestamp, description) VALUES (?, ?)"

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    try:
        cursor.execute(command, (utctime, logMessage))
    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()



def executeCommand(command):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    # execute
    cursor.execute(command)
    connection.commit()

    # close
    connection.close()



def storeBook(book):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    addedToSql = datetime.utcnow()

    command = "INSERT INTO books (addedToSql, \
            idn, linkToDataset, \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            lastDnbTransaction, projectedPublicationDate, \
            title, subTitle, titleAuthor, \
            authorName, \
            publicationPlace, publisher, publicationYear) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    newBookWasAdded = False

    try:
        cursor.execute(command, \
            (addedToSql, \
            book.idn, book.linkToDataset,  \
            book.isbns[0].withDashes, book.isbns[0].noDashes, book.isbns[0].termsOfAvailability, \
            book.lastDnbTransaction, book.projectedPublicationDate, \
            book.title, book.subTitle, book.titleAuthor, \
            book.authorName, \
            book.publicationPlace, book.publisher, book.publicationYear)
            )

        print(f"Adding new book. Title: {book.title}")
        newBookWasAdded = True

    except Exception as e:
        #print(e)
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
