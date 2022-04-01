import mariaDatabase
import uuid
from datetime import datetime

########## Logbook
def createLogbook():
    # Create logbook
    command = """
    CREATE TABLE IF NOT EXISTS logbook (id CHAR(36) PRIMARY KEY, timestamp TIMESTAMP, description VARCHAR(128))
    """
    mariaDatabase.executeCommand(command)



def addUUIDsToLogbook():

    # connect    
    connection = mariaDatabase.getDatabaseConnection()
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
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()   

    try:
        cursor.execute(command, (utctime, newUUID, logMessage))
    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()