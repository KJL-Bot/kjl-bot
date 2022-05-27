import mariaDatabase
import uuid
from datetime import datetime

########## Logbook
def createLogbook():
    # Create logbook
    command = """
    CREATE TABLE IF NOT EXISTS logbook (id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP, description VARCHAR(128))
    """
    mariaDatabase.executeCommand(command)

def createInitialLogbookMessage():

    utctime = datetime.utcnow()
    description = "Scraping DNB"

    command = "INSERT INTO logbook (timestamp, description) VALUES (?, ?)"

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # add new message
    try:
        cursor.execute(command, (utctime, description))
    except Exception as e:
        print(e)

    connection.commit()

    # get ID of the message we just created
    lastRowId = cursor.lastrowid

    # close
    connection.close()

    # return the id of the log message we just created
    return lastRowId


# Updates log message text for given messageId.
def updateLogbookMessageWithId(messageId, logMessage):

    utctime = datetime.utcnow()

    command = "UPDATE logbook SET (timestamp, description) VALUES (?, ?) WHERE id = ?"

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    try:
        cursor.execute(command, (utctime, logMessage, messageId))
    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()


# probably obsolete
def logMessage(logMessage):

    utctime = datetime.utcnow()
    #newUUID = str(uuid.uuid4())

    #timezone = pytz.utc
    #utctime = timezone.localiz(utctime)

    command = "INSERT INTO logbook (timestamp, description) VALUES (?, ?)"

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    try:
        cursor.execute(command, (utctime, UUID, logMessage))
    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()
