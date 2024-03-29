import mariaDatabase
import mariadb
from datetime import datetime, timedelta
import logbookManager
from dateutil.relativedelta import relativedelta
import config
import reviewManager

######## Books

def createBooksTable():

    # Create books table. Copied from Sequel Pro on 2023-06-16
    command = """
CREATE TABLE IF NOT EXISTS `books` (
  `idn` varchar(10) NOT NULL,
  `linkToDataset` varchar(128) DEFAULT NULL,
  `isbnWithDashes` varchar(20) DEFAULT NULL,
  `isbnNoDashes` varchar(20) DEFAULT NULL,
  `isbnTermsOfAvailability` varchar(512) DEFAULT NULL,
  `addedToSql` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `updatedInSql` timestamp NULL DEFAULT NULL,
  `lastDnbTransaction` timestamp NULL DEFAULT NULL,
  `projectedPublicationDate` timestamp NULL DEFAULT NULL,
  `title` varchar(1024) DEFAULT NULL,
  `subTitle` varchar(1024) DEFAULT NULL,
  `titleAuthor` varchar(1024) DEFAULT NULL,
  `authorName` varchar(256) DEFAULT NULL,
  `secondaryAuthorName` varchar(256) DEFAULT NULL,
  `sortingAuthor` varchar(256) DEFAULT NULL,
  `keywords` varchar(1024) DEFAULT NULL,
  `keywords653` varchar(8192) DEFAULT NULL,
  `genre655_0` varchar(128) DEFAULT NULL,
  `genre655_a` varchar(256) DEFAULT NULL,
  `genre655_2` varchar(128) DEFAULT NULL,
  `publicationPlace` varchar(128) DEFAULT NULL,
  `publisher` varchar(256) DEFAULT NULL,
  `publicationYear` varchar(64) DEFAULT NULL,
  `matchesRelevantPublisher` mediumint(11) DEFAULT NULL,
  `publisherJLPNominated` tinyint(1) DEFAULT NULL,
  `publisherJLPAwarded` tinyint(1) DEFAULT NULL,
  `publisherKimiAwarded` tinyint(1) DEFAULT NULL,
  `bookIsRelevant` tinyint(1) DEFAULT NULL,
  `logbookMessageId` mediumint(9) DEFAULT NULL,
  PRIMARY KEY (`idn`),
  KEY `logbookMessageId` (`logbookMessageId`),
  KEY `isbnWithDashes` (`isbnWithDashes`),
  FULLTEXT KEY `sortingAuthor` (`sortingAuthor`),
  FULLTEXT KEY `titleIndex` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """




    #command = """
    #CREATE TABLE IF NOT EXISTS books (
    #    idn VARCHAR(10) PRIMARY KEY,
    #   linkToDataset VARCHAR(128),

    #    isbnWithDashes VARCHAR(20),
    #    isbnNoDashes VARCHAR(20),
    #    isbnTermsOfAvailability VARCHAR(512),

    #    addedToSql TIMESTAMP,
    #    updatedInSql TIMESTAMP,

    #    lastDnbTransaction TIMESTAMP,
    #    projectedPublicationDate TIMESTAMP,

    #    title VARCHAR(1024),
    #    subTitle VARCHAR(1024),
    #    titleAuthor VARCHAR(1024),

    #    authorName VARCHAR(256),
    #    secondaryAuthorName VARCHAR(128),
    #    sortingAuthor VARCHAR(128),

    #    keywords VARCHAR(1024),
    #    keywords653 VARCHAR(4096),

    #    genre655_0 VARCHAR(128),
    #    genre655_a VARCHAR(256),
    #    genre655_2 VARCHAR(128),

    #    publicationPlace VARCHAR(128),
    #    publisher VARCHAR(256),
    #    publicationYear VARCHAR(64),

    #    matchesRelevantPublisher MEDIUMINT,
    #    publisherJLPNominated TINYINT,
    #    publisherJLPAwarded TINYINT,
    #    publisherKimiAwarded TINYINT,

    #    bookIsRelevant TINYINT,
    #    logbookMessageId MEDIUMINT,

    #    INDEX(logbookMessageId),
    #    INDEX(isbnWithDashes),
    #    INDEX(title)

    #);"""


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
            logbookManager.logMessage(relatesToIDN=book.idn, description=f"Added new book with title: '{book.title}'")
            returnValue = "inserted"
        else:
            logbookManager.logMessage(relatesToIDN=book.idn, description=f"Failed to add new book with IDN: '{book.idn}'")

    # if not, update entry
    else:

        # were any of the fields updated?
        numberOfUpdatedFields = identifyUpdatedFields(book, matchingDBEntry)

        # if so...
        if numberOfUpdatedFields > 0:

            # update book in the database
            success = updateBook(book, logbookMessageId)

            # write to logbook
            if success:
                logbookManager.logMessage(relatesToIDN=book.idn, description=f"Updated {numberOfUpdatedFields} fields for book with title: '{book.title}'")
                returnValue = "updated"
            else:
                logbookManager.logMessage(relatesToIDN=book.idn, description=f"Failed to update book with IDN: '{book.idn}'")

    return returnValue

# if field values change, log a message to logbook
def logFieldMismatch(idn, fieldName, dbValue, bookValue):
    if dbValue != bookValue:
        message = f"IDN {idn}: {fieldName}: (XML) {bookValue} -> (DB) {dbValue}"
        logbookManager.logMessage(relatesToIDN=idn, description=message)
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

    # keywords653
    keywords653 = None
    if len(book.keywords653) > 0:
        keywords653 = ','.join(book.keywords653)
    counter += logFieldMismatch(idn = book.idn, fieldName = "keywords653", dbValue = matchingDBEntry["keywords653"], bookValue = keywords653)

    # genre655_0
    genre655_0 = book.genre655_0
    counter += logFieldMismatch(idn = book.idn, fieldName = "genre655_0", dbValue = matchingDBEntry["genre655_0"], bookValue = genre655_0)

    # genre655_a
    genre655_a = book.genre655_a
    counter += logFieldMismatch(idn = book.idn, fieldName = "genre655_a", dbValue = matchingDBEntry["genre655_a"], bookValue = genre655_a)

    # genre655_2
    genre655_2 = book.genre655_2
    counter += logFieldMismatch(idn = book.idn, fieldName = "genre655_2", dbValue = matchingDBEntry["genre655_2"], bookValue = genre655_2)

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

    keywords653 = None
    if len(book.keywords653) > 0:
        keywords653 = ','.join(book.keywords653)


    command = "INSERT INTO books (idn, linkToDataset, \
            isbnWithDashes, isbnNoDashes, isbnTermsOfAvailability, \
            addedToSql, \
            lastDnbTransaction, projectedPublicationDate, \
            title, subTitle, titleAuthor, \
            authorName, secondaryAuthorName, sortingAuthor,\
            keywords, keywords653, genre655_0, genre655_a, genre655_2,\
            publicationPlace, publisher, publicationYear, logbookMessageId) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


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
            keywords, keywords653, book.genre655_0, book.genre655_a, book.genre655_2,\
            book.publicationPlace, book.publisher, book.publicationYear, logbookMessageId)
            )

        success = True


    # ignore feedback on violation of UNIQUE contraint
    except mariadb.IntegrityError:
        pass

    # other errors
    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        logbookManager.logMessage(relatesToIDN=book.idn, description=f"storeBook: {type(e).__name__} was raised with error number: {e}")
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

    keywords653 = None
    if len(book.keywords653) > 0:
        keywords653 = ','.join(book.keywords653)

    command = "UPDATE books SET \
            isbnWithDashes = ?, isbnNoDashes = ?, isbnTermsOfAvailability = ?, \
            updatedInSql = ?, \
            lastDnbTransaction = ?, projectedPublicationDate = ?, \
            title = ?, subTitle = ?, titleAuthor = ?, \
            authorName = ?, secondaryAuthorName = ?, sortingAuthor = ?,\
            keywords = ?, keywords653 = ?, genre655_0 = ?, genre655_a = ?, genre655_2 = ?, \
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
            keywords, keywords653, book.genre655_0, book.genre655_a, book.genre655_2,\
            book.publicationPlace, book.publisher, book.publicationYear, \
            logbookMessageId,
            book.idn)
            )

        success = True

    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        logbookManager.logMessage(relatesToIDN=book.idn, description=f"updateBook: {type(e).__name__} was raised with error number: {e}")
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
    firstDayOfThisMonth = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    firstDayOfNextMonth = firstDayOfThisMonth + relativedelta(months=1)
    firstDayOfFirstValidMonth = firstDayOfThisMonth - relativedelta(months=1)

    # get all available reviews from dB
    availableReviews = reviewManager.getReviews()

    # connect to DB
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # name of the books table
    booksTableName = config.booksTableName

    # get fields to deternmine whether book is relevant
    command = f"SELECT idn, isbnWithDashes, projectedPublicationDate, matchesRelevantPublisher, title, sortingAuthor FROM {booksTableName} ORDER BY idn DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    # go through all books int the DB
    for (idn, isbnWithDashes, projectedPublicationDate, matchesRelevantPublisher, title, sortingAuthor) in books:

        # default: book is relevant
        bookIsRelevant = True

        # skip entries without ISDN
        if isbnWithDashes is None:
            bookIsRelevant = False

        # skip entries that do not have a sortingAuthor
        if sortingAuthor is None:
            bookIsRelevant = False

        # if there is no projectedPublicationDate...
        if projectedPublicationDate is None:
            bookIsRelevant = False

        # skip entries whose projected publication date is too far in the future
        if (projectedPublicationDate is None) or (projectedPublicationDate > firstDayOfNextMonth) or (projectedPublicationDate < firstDayOfFirstValidMonth):
            bookIsRelevant = False

        ###### Override #####

        # if there is a review, overide everything and mark the book as relevant
        matchingReviews = reviewManager.matchingReviewsForIdn(idn, availableReviews)
        if len(matchingReviews) > 0:
            bookIsRelevant = True

        # write to DB
        command = f"UPDATE {booksTableName} SET bookIsRelevant = ? WHERE idn = ?"
        try:
            cursor.execute(command, (bookIsRelevant, idn))
        except Exception as e:
            print(e)

    connection.commit()


    connection.close()
