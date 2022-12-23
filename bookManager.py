import mariaDatabase
import mariadb
from datetime import datetime, timedelta
import logbookManager
from dateutil.relativedelta import relativedelta
import config

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

        title VARCHAR(512),
        subTitle VARCHAR(512),
        titleAuthor VARCHAR(512),

        authorName VARCHAR(256),
        secondaryAuthorName VARCHAR(128),
        sortingAuthor VARCHAR(128),

        keywords VARCHAR(1024),

        publicationPlace VARCHAR(128),
        publisher VARCHAR(256),
        publicationYear VARCHAR(64),

        matchesRelevantPublisher MEDIUMINT,
        publisherJLPNominated TINYINT,
        publisherJLPAwarded TINYINT,
        publisherKimiAwarded TINYINT,

        bookIsRelevant TINYINT,
        logbookMessageId MEDIUMINT,

        INDEX(logbookMessageId)

    );"""

    mariaDatabase.executeCommand(command)


def insertOrUpdateBook(book, logbookMessageId):

    returnValue = None

    # is the book already in the DB?
    matchingDBEntry = findMatchingBookInDB(book)

    # if not, store it
    if matchingDBEntry is None:

        # store
        success = storeBook(book, logbookMessageId)

        # write to logbook
        if success:
            logbookManager.logMessage(f"Added new book with title: '{book.title}'")
            returnValue = "inserted"
        else:
            logbookManager.logMessage(f"Failed to add new book with IDN: '{book.idn}'")

    # if not, update entry
    else:

        # where any of the fields updated?
        numberOfUpdatedFields = identifyUpdatedFields(book, matchingDBEntry)

        # if so...
        if numberOfUpdatedFields > 0:

            # update book in the database
            success = updateBook(book, logbookMessageId)

            # write to logbook
            if success:
                logbookManager.logMessage(f"Updated {numberOfUpdatedFields} fields for book with title: '{book.title}'")
                returnValue = "updated"
            else:
                logbookManager.logMessage(f"Failed to update book with IDN: '{book.idn}'")

    return returnValue

# if field values change, log a message to logbook
def logFieldMismatch(idn, fieldName, dbValue, bookValue):
    if dbValue != bookValue:
        message = f"IDN {idn}: {fieldName}: {dbValue} -> {bookValue}"
        logbookManager.logMessage(message)
        return 1

    else:
        return 0

# go through all fields and identify those which were updated
def identifyUpdatedFields(book, matchingDBEntry):

    counter = 0

    # isbnWithDashes
    isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
    counter += logFieldMismatch(idn = book.idn, fieldName = "isbnWithDashes", dbValue = matchingDBEntry["isbnWithDashes"], bookValue = isbnWithDashes)

    # isbnNoDashes
    isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
    counter += logFieldMismatch(idn = book.idn, fieldName = "isbnNoDashes", dbValue = matchingDBEntry["isbnNoDashes"], bookValue = isbnNoDashes)

    # isbnTermsOfAvailability
    isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None
    counter += logFieldMismatch(idn = book.idn, fieldName = "isbnTermsOfAvailability", dbValue = matchingDBEntry["isbnTermsOfAvailability"], bookValue = isbnTermsOfAvailability)

    # book.lastDnbTransaction
    lastDnbTransaction = book.lastDnbTransaction
    counter += logFieldMismatch(idn = book.idn, fieldName = "lastDnbTransaction", dbValue = matchingDBEntry["lastDnbTransaction"], bookValue = lastDnbTransaction)

    # book.projectedPublicationDate
    projectedPublicationDate = book.projectedPublicationDate
    counter += logFieldMismatch(idn = book.idn, fieldName = "projectedPublicationDate", dbValue = matchingDBEntry["projectedPublicationDate"], bookValue = projectedPublicationDate)

    # book.title
    title = book.title
    counter += logFieldMismatch(idn = book.idn, fieldName = "title", dbValue = matchingDBEntry["title"], bookValue = title)

    # book.subTitle
    subTitle = book.subTitle
    counter += logFieldMismatch(idn = book.idn, fieldName = "subTitle", dbValue = matchingDBEntry["subTitle"], bookValue = subTitle)

    # book.titleAuthor
    titleAuthor = book.titleAuthor
    counter += logFieldMismatch(idn = book.idn, fieldName = "titleAuthor", dbValue = matchingDBEntry["titleAuthor"], bookValue = titleAuthor)

    # book.authorName
    authorName = book.authorName
    counter += logFieldMismatch(idn = book.idn, fieldName = "authorName", dbValue = matchingDBEntry["authorName"], bookValue = authorName)

    # book.secondaryAuthorName
    secondaryAuthorName = book.secondaryAuthorName
    counter += logFieldMismatch(idn = book.idn, fieldName = "secondaryAuthorName", dbValue = matchingDBEntry["secondaryAuthorName"], bookValue = secondaryAuthorName)

    # book.sortingAuthor
    sortingAuthor = book.sortingAuthor
    counter += logFieldMismatch(idn = book.idn, fieldName = "sortingAuthor", dbValue = matchingDBEntry["sortingAuthor"], bookValue = sortingAuthor)

    # keywords
    keywords = None
    if len(book.keywords) > 0:
        keywords = ','.join(book.keywords)
    counter += logFieldMismatch(idn = book.idn, fieldName = "keywords", dbValue = matchingDBEntry["keywords"], bookValue = keywords)

    # book.publicationPlace
    publicationPlace = book.publicationPlace
    counter += logFieldMismatch(idn = book.idn, fieldName = "publicationPlace", dbValue = matchingDBEntry["publicationPlace"], bookValue = publicationPlace)

    # book.publisher
    publisher = book.publisher
    counter += logFieldMismatch(idn = book.idn, fieldName = "publisher", dbValue = matchingDBEntry["publisher"], bookValue = publisher)

    # book.publicationYear
    publicationYear = book.publicationYear
    counter += logFieldMismatch(idn = book.idn, fieldName = "publicationYear", dbValue = matchingDBEntry["publicationYear"], bookValue = publicationYear)

    # return the number of updated logFieldMismatch
    return counter


def findMatchingBookInDB(book):

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor(dictionary=True)

    sqlCommand = "SELECT * FROM books WHERE idn = ?"

    try:
        cursor.execute(sqlCommand, (book.idn,))
    except Exception as e:
        print(e)

    matches = cursor.fetchall()

    matchingBook = None
    if len(matches) > 0:
        matchingBook = matches[0]

    # close
    connection.commit()
    connection.close()

    return matchingBook


def storeBook(book, logbookMessageId):

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    timestamp = datetime.utcnow()

    # extract ISBN
    isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
    isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
    isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None

    # concatenate keywords in array to a string
    keywords = None
    if len(book.keywords) > 0:
        keywords = ','.join(book.keywords)

    command = "INSERT INTO books (idn, linkToDataset, \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            addedToSql, \
            lastDnbTransaction, projectedPublicationDate, \
            title, subTitle, titleAuthor, \
            authorName, secondaryAuthorName, sortingAuthor,\
            keywords, \
            publicationPlace, publisher, publicationYear, logbookMessageId) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


    success = False

    # try inserting new book
    try:
        cursor.execute(command, \
            (book.idn, book.linkToDataset,  \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            timestamp,\
            book.lastDnbTransaction, book.projectedPublicationDate, \
            book.title, book.subTitle, book.titleAuthor, \
            book.authorName, book.secondaryAuthorName, book.sortingAuthor,\
            keywords, \
            book.publicationPlace, book.publisher, book.publicationYear, logbookMessageId)
            )

        success = True


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

    return success



def updateBook(book, logbookMessageId):

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    timestamp = datetime.utcnow()

    # extract ISBN
    isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
    isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
    isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None

    # concatenate keywords in array to a string
    keywords = None
    if len(book.keywords) > 0:
        keywords = ','.join(book.keywords)


    command = "UPDATE books SET \
            isbnWithDashes = ?, isbnNoDashes = ?, isbnTermsOfAvailability = ?, \
            updatedInSql = ?, \
            lastDnbTransaction = ?, projectedPublicationDate = ?, \
            title = ?, subTitle = ?, titleAuthor = ?, \
            authorName = ?, secondaryAuthorName = ?, sortingAuthor = ?,\
            keywords = ?, \
            publicationPlace = ?, publisher = ?, publicationYear = ?, \
            logbookMessageId = ? \
            WHERE idn = ?"

    success = False

    # try updating book
    try:
        cursor.execute(command, \
            (isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            timestamp,\
            book.lastDnbTransaction, book.projectedPublicationDate, \
            book.title, book.subTitle, book.titleAuthor, \
            book.authorName, book.secondaryAuthorName, book.sortingAuthor,\
            keywords, \
            book.publicationPlace, book.publisher, book.publicationYear, \
            logbookMessageId,
            book.idn)
            )

        success = True

    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        print("Error while updating book:")
        print(book.linkToDataset)
        print(book.publicationYear)
        pass

    # close
    connection.commit()
    connection.close()

    return success

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


def identifyRelevantBooks():

    # get data limit
    now = datetime.utcnow()
    firstDayOfNextMonth = now.replace(day=1) + relativedelta(months=1)

    # connect to DB
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # name of the books table
    booksTableName = config.booksTableName

    # get fields to deternmine whether book is relevant
    command = f"SELECT idn, isbnWithDashes, projectedPublicationDate, matchesRelevantPublisher, title, titleAuthor FROM {booksTableName} ORDER BY idn DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    # go through all books int the DB
    for (idn, isbnWithDashes, projectedPublicationDate, matchesRelevantPublisher, title, titleAuthor) in books:

        # default: book is relevant
        bookIsRelevant = True

        # skip entries without ISDN
        if isbnWithDashes is None:
            bookIsRelevant = False

        # skip entries that do not have a titleAuthor
        if titleAuthor is None:
            bookIsRelevant = False

        # skip entries without expected publication date
        if projectedPublicationDate is None:
            bookIsRelevant = False

        # skip entries whose projected publication date is too far in the future
        if projectedPublicationDate is None or projectedPublicationDate > firstDayOfNextMonth:
            bookIsRelevant = False

        # write to DB
        command = f"UPDATE {booksTableName} SET bookIsRelevant = ? WHERE idn = ?"
        try:
            cursor.execute(command, (bookIsRelevant, idn))
        except Exception as e:
            print(e)

    connection.commit()


    connection.close()


# def insertOrUpdateBook(book, logbookMessageId):
#
#     # connect
#     connection = mariaDatabase.getDatabaseConnection()
#     cursor = connection.cursor()
#
#     currentTimestamp = datetime.utcnow()
#
#     # command = "INSERT INTO books (addedToSql, \
#     #         idn, linkToDataset, \
#     #         isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
#     #         lastDnbTransaction, projectedPublicationDate, \
#     #         title, subTitle, titleAuthor, \
#     #         authorName, secondaryAuthorName, sortingAuthor,\
#     #         keywords, \
#     #         publicationPlace, publisher, publicationYear, logbookMessageId) \
#     #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
#
#     # by default, no new book was added
#     newBookWasAdded = False
#
#     # extract ISBN
#     isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
#     isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
#     isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None
#
#     # concatenate keywords in array to a string
#     keywords = None
#     if len(book.keywords) > 0:
#         keywords = ','.join(book.keywords)
#
#     sqlCommand = f"""
#         INSERT INTO books SET
#             idn = {book.idn},
#             linkToDataset = '{book.linkToDataset}',
#
#             isbnWithDashes = '{isbnWithDashes}',
#             isbnNoDashes = '{isbnNoDashes}',
#             isbnTermsOfAvailability = '{isbnTermsOfAvailability}',
#
#             addedToSql = '{currentTimestamp}',
#             updatedInSql = '{currentTimestamp}',
#
#             lastDnbTransaction = '{book.lastDnbTransaction}',
#             projectedPublicationDate = '{book.projectedPublicationDate}',
#
#             title = '{book.title}',
#             subTitle = '{book.subTitle}',
#             titleAuthor = '{book.titleAuthor}',
#
#             authorName = '{book.authorName}',
#             secondaryAuthorName = '{book.secondaryAuthorName}',
#             sortingAuthor = '{book.sortingAuthor}',
#
#             keywords = '{keywords}',
#
#             publicationPlace = '{book.publicationPlace}',
#             publisher = '{book.publisher}',
#             publicationYear = '{book.publicationYear}',
#
#             logbookMessageId = {logbookMessageId}
#
#
#             ON DUPLICATE KEY UPDATE
#
#             isbnWithDashes = '{isbnWithDashes}',
#             isbnNoDashes = '{isbnNoDashes}',
#             isbnTermsOfAvailability = '{isbnTermsOfAvailability}',
#
#             updatedInSql = '{currentTimestamp}',
#
#             lastDnbTransaction = '{book.lastDnbTransaction}',
#             projectedPublicationDate = '{book.projectedPublicationDate}',
#
#             title = '{book.title}',
#             subTitle = '{book.subTitle}',
#             titleAuthor = '{book.titleAuthor}',
#
#             authorName = '{book.authorName}',
#             secondaryAuthorName = '{book.secondaryAuthorName}',
#             sortingAuthor = '{book.sortingAuthor}',
#
#             keywords = '{keywords}',
#
#             publicationPlace = '{book.publicationPlace}',
#             publisher = '{book.publisher}',
#             publicationYear = '{book.publicationYear}'
#
#     """
#
#     # try inserting new book
#     try:
#         cursor.execute(sqlCommand)
#
#         print(f"Adding new book. Title: {book.title}")
#         newBookWasAdded = True
#
#     # ignore feedback on violation of UNIQUE contraint
#     except mariadb.IntegrityError:
#         pass
#
#     # other errors
#     except Exception as e:
#         print(f"{type(e).__name__} was raised with error number: {e}")
#         print("Error while inserting new book:")
#         print(book.linkToDataset)
#         print(book.publicationYear)
#         pass
#
#     # close
#     connection.commit()
#     connection.close()
#
#     return newBookWasAdded


# def storeBook(book, logbookMessageId):
#
#     # connect
#     connection = mariaDatabase.getDatabaseConnection()
#     cursor = connection.cursor()
#
#     timestamp = datetime.utcnow()
#
#     command = "INSERT INTO books (idn, linkToDataset, \
#             isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
#             addedToSql, \
#             lastDnbTransaction, projectedPublicationDate, \
#             title, subTitle, titleAuthor, \
#             authorName, secondaryAuthorName, sortingAuthor,\
#             keywords, \
#             publicationPlace, publisher, publicationYear, logbookMessageId) \
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
#
#     # by default, no new book was added
#     newBookWasAdded = False
#
#     # extract ISBN
#     isbnWithDashes = book.isbns[0].withDashes if len(book.isbns) > 0 else None
#     isbnNoDashes = book.isbns[0].noDashes if len(book.isbns) > 0 else None
#     isbnTermsOfAvailability = book.isbns[0].termsOfAvailability if len(book.isbns) > 0 else None
#
#     # concatenate keywords in array to a string
#     keywords = None
#     if len(book.keywords) > 0:
#         keywords = ','.join(book.keywords)
#
#     # try inserting new book
#     try:
#         cursor.execute(command, \
#             (book.idn, book.linkToDataset,  \
#             isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
#             timestamp,\
#             book.lastDnbTransaction, book.projectedPublicationDate, \
#             book.title, book.subTitle, book.titleAuthor, \
#             book.authorName, book.secondaryAuthorName, book.sortingAuthor,\
#             keywords, \
#             book.publicationPlace, book.publisher, book.publicationYear, logbookMessageId)
#             )
#
#         print(f"Adding new book. Title: {book.title}")
#         newBookWasAdded = True
#
#     # ignore feedback on violation of UNIQUE contraint
#     except mariadb.IntegrityError:
#         pass
#
#     # other errors
#     except Exception as e:
#         print(f"{type(e).__name__} was raised with error number: {e}")
#         print("Error while inserting new book:")
#         print(book.linkToDataset)
#         print(book.publicationYear)
#         pass
#
#     # close
#     connection.commit()
#     connection.close()
#
#     return newBookWasAdded
