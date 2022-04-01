import mariaDatabase
import mariadb
from datetime import datetime, timedelta


######## Books

def createBooksTable():

    # Create books table
    command = """
    CREATE TABLE IF NOT EXISTS books (
        idn VARCHAR(10) PRIMARY KEY, 
        linkToDataset VARCHAR(128),
        
        isbnWithDashes VARCHAR(20), 
        isbnNoDashes VARCHAR(20), 
        isbnTermsOfAvailability VARCHAR(256), 

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
        publicationYear VARCHAR(16),

        matchesRelevantPublisher MEDIUMINT,
        logbookMessageId MEDIUMINT

    );"""

    mariaDatabase.executeCommand(command)



def storeBook(book, logbookMessageId):

    # connect    
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()   

    addedToSql = datetime.utcnow()

    command = "INSERT INTO books (addedToSql, \
            idn, linkToDataset, \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            lastDnbTransaction, projectedPublicationDate, \
            title, subTitle, titleAuthor, \
            authorName, \
            publicationPlace, publisher, publicationYear, logbookMessageId) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    newBookWasAdded = False
    isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
    isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
    isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None

    try:
        cursor.execute(command, \
            (addedToSql,\
            book.idn, book.linkToDataset,  \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            book.lastDnbTransaction, book.projectedPublicationDate, \
            book.title, book.subTitle, book.titleAuthor, \
            book.authorName, \
            book.publicationPlace, book.publisher, book.publicationYear, logbookMessageId)
            )

        print(f"Adding new book. Title: {book.title}")
        newBookWasAdded = True

    # ignore feedback on violation of UNIQUE contraint
    except mariadb.IntegrityError:
        pass

    # other errors
    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        print("Error while inserting new book:")
        print(book.linkToDataset)
        print(book.publicationYear)
        pass

    # close
    connection.commit()
    connection.close()

    return newBookWasAdded

def displayBookContent():

    # connect    
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()   

    command = "SELECT logbookMessageId, idn, isbnWithDashes, DATETIME(addedToSql), DATETIME(lastDnbTransaction), DATE(projectedPublicationDate), publicationYear, authorName, title  FROM books ORDER BY idn DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    for book in books:
        print(book)
    

    connection.close()
