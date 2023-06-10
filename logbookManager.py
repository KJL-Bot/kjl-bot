import mariaDatabase
import uuid
from datetime import datetime
import config

# use this message command to log a scrape for a particular year
scrapeForYearCommand = config.scrapeForYearCommand

########## Logbook
def createLogbook():
    # Create logbook
    command = """
    CREATE TABLE IF NOT EXISTS logbook (id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        timestamp TIMESTAMP,
        command VARCHAR(64),
        parameter VARCHAR(64),
        relatesToIDN VARCHAR(10),
        description VARCHAR(512),
        INDEX command (command))
    """
    mariaDatabase.executeCommand(command)

# creates a specific log message to remember the year for which a scrape is being carried out
def logScrapeStart(year):
    command = scrapeForYearCommand
    parameter = year
    description = ""

    messageId = createLogbookMessage(command=command, parameter=parameter,  relatesToIDN=None, description=description)
    return messageId

# retrieves the year of the youngest scrape
def getLastScrapeYearFromLogbook():

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # the parameter of the youngest {scrapeForYearCommand} is the lastScrapeYear
    command = f"SELECT parameter FROM logbook WHERE command = '{scrapeForYearCommand}' ORDER BY id DESC"
    cursor.execute(command)
    result = cursor.fetchall()

    # close
    connection.close()

    lastScrapeYear = None
    if len(result) > 0:
        (lastScrapeYear,) = result[0]
        lastScrapeYear = int(lastScrapeYear)

    return lastScrapeYear

# for which year should the next scrape be done?
def determineNextScrapeYear(numberOfYearsToScrape):

    currentYear = datetime.today().year

    # we go one year into the future
    finalYearToScrape = currentYear + 1

    # we go back {numberOfYearsToScrape} number of years
    firstYearToScrape = finalYearToScrape - numberOfYearsToScrape + 1

    # which year did we scrape previously?
    yearOfPreviousScrape = getLastScrapeYearFromLogbook()

    # by default, start with {firstYearToScrape}
    nextYearToScrape = firstYearToScrape

    # in case we a previous scrape
    if yearOfPreviousScrape is not None:
        # set scrape to the following year
        nextYearToScrape = yearOfPreviousScrape + 1

        # make sure that we don't exceed finalYearToScrape
        if nextYearToScrape > finalYearToScrape:
            nextYearToScrape = firstYearToScrape

    # return result
    return nextYearToScrape

def logRecordRetrieval(numberOfRecords):

    command = "retrievedRecords"
    parameter = numberOfRecords
    relatesToIDN = None
    description = f"Retrieved {numberOfRecords} DNB records"

    messageId = createLogbookMessage(command=command, parameter=parameter, relatesToIDN=relatesToIDN, description=description)
    return messageId

def logBooksAddition(numberOfBooks):

    command = "addedBooks"
    parameter = numberOfBooks
    relatesToIDN = None
    description = f"Added {numberOfBooks} books to database"

    messageId = createLogbookMessage(command=command, parameter=parameter, relatesToIDN=relatesToIDN, description=description)
    return messageId

def logBooksUpdate(numberOfBooks):

    command = "updatedBooks"
    parameter = numberOfBooks
    relatesToIDN = None
    description = f"Updated {numberOfBooks} books in database"

    messageId = createLogbookMessage(command=command, parameter=parameter, relatesToIDN=relatesToIDN, description=description)
    return messageId

def logUnmatchedReview(reviewId):

    command = "unmatchedReview"
    parameter = reviewId
    relatesToIDN = None
    description = f"Unable to match review with id {reviewId}"

    messageId = createLogbookMessage(command=command, parameter=parameter, relatesToIDN=relatesToIDN, description=description)
    return messageId

# Log simple message
def logMessage(relatesToIDN, description):

    #utctime = datetime.utcnow()
    command = "logMessage"
    parameter = None
    description = description

    messageId = createLogbookMessage(command=command, parameter=parameter, relatesToIDN=relatesToIDN, description=description)
    return messageId

# Main function to log message
def createLogbookMessage(command, parameter, relatesToIDN, description):

    # current time
    utctime = datetime.utcnow()

    # print
    print(f"{utctime}\t{command}\t{parameter}\t{relatesToIDN}\t{description}")

    # command
    sqlCommand = "INSERT INTO logbook (timestamp, command, parameter, relatesToIDN, description) VALUES (?, ?, ?, ?, ?)"

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # add new message
    try:
        cursor.execute(sqlCommand, (utctime, command, parameter, relatesToIDN, description))
    except Exception as e:
        print(f"createLogbookMessage: {e}")

    connection.commit()

    # get ID of the message we just created
    lastRowId = cursor.lastrowid

    # close
    connection.close()

    # return the id of the log message we just created
    return lastRowId
