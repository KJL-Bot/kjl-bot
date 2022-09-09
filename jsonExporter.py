import mariaDatabase
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import config
from pathlib import Path
import utilities

def generateValidBookEntries(numberOfDesiredBooks):

    # contains the  data for all the valid books
    bookArray = []

    # count the number of valid books
    bookCounter = 0

    # the first day of the month following  this month (eg. March if we are in Februray)
    now = datetime.utcnow()
    firstDayOfNextMonth = now.replace(day=1) + relativedelta(months=1)

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # get logbook entries
    command = "SELECT timestamp, id, description  FROM logbook ORDER BY timestamp DESC"
    cursor.execute(command)
    logbookEntries = cursor.fetchall()

    # go through each entry
    for logbookEntry in logbookEntries:

        (logBookTimestamp, logBookId, logBookDescription) = logbookEntry

        command = "SELECT idn, isbnWithDashes, title, subTitle, titleAuthor, keywords, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset, matchesRelevantPublisher, publisherJLPNominated, publisherJLPAwarded, publisherKimiAwarded " +\
            "FROM books WHERE bookIsRelevant = 1 AND logbookMessageId = ? ORDER BY idn DESC"

        try:
            cursor.execute(command, (logBookId, ))
            books = cursor.fetchall()


            for (idn, isbnWithDashes, title, subTitle, titleAuthor, keywords, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset, matchesRelevantPublisher, publisherJLPNominated, publisherJLPAwarded, publisherKimiAwarded) in books:

                # filtering no longer necessary, as filtering is done through bookIsRelevant field

                # # skip entries without ISDN
                # if isbnWithDashes is None:
                #     continue
                #
                # # skip entries without expected publication date
                # if projectedPublicationDate is None:
                #     continue
                #
                # # skip entries whose projected publication date is too far in the future
                # if projectedPublicationDate > firstDayOfNextMonth:
                #     continue

                # here we know that the book is a valid entry. Create a book.
                book = {}

                # add to dictionary if data is available
                book["idn"] = idn
                if title is not None: book["title"] = title
                if subTitle is not None: book["subTitle"] = subTitle
                if titleAuthor is not None: book["titleAuthor"] = titleAuthor
                book["keywords"] = keywords if keywords is not None else ""
                if publicationPlace is not None: book["publicationPlace"] = publicationPlace
                if publisher is not None: book["publisher"] = publisher
                if publicationYear is not None: book["publicationYear"] = publicationYear
                if projectedPublicationDate is not None: book["projectedPublicationDate"] = projectedPublicationDate.strftime('%Y-%m-%d')
                if linkToDataset is not None: book["linkToDataset"] = linkToDataset
                if isbnWithDashes is not None: book["isbnWithDashes"] = isbnWithDashes
                if addedToSql is not None: book["addedToSql"] = addedToSql.strftime('%Y-%m-%dT%H:%M:%SZ')
                if matchesRelevantPublisher is not None: book["matchesRelevantPublisher"] = matchesRelevantPublisher
                book["publisherJLPNominated"] = publisherJLPNominated if publisherJLPNominated is not None else 0
                book["publisherJLPAwarded"] = publisherJLPAwarded if publisherJLPAwarded is not None else 0
                book["publisherKimiAwarded"] = publisherKimiAwarded if publisherKimiAwarded is not None else 0

                # add cover url
                if isbnWithDashes is not None: book["coverUrl"] = utilities.coverUrl(isbnWithDashes=isbnWithDashes, size='l')

                # count the book.
                bookCounter += 1

                # Add the book as long as the limit is not reached
                if bookCounter <= numberOfDesiredBooks:
                    bookArray.append(book)



        except Exception as e:
            print(f"Fehler beim suchen der Bücher für logbook Entry mit id {logBookId}.")
            print(e)


    connection.close()

    return bookArray

def writeBookEntriesToJSONFile(bookEntries):

    with open(config.recentBooksJsonFileName, 'w', encoding='utf-8') as f:
        json.dump(bookEntries, f, indent=2, ensure_ascii=False)

    return Path(config.recentBooksJsonFileName)

if __name__ == '__main__':
    validBookEntries = generateValidBookEntries(1000)
    jsonFileName = writeBookEntriesToJSONFile(validBookEntries)
    print(f"JSON data written to {jsonFileName}")
