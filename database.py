import sqlite3

databaseName = "kjl.db"

def createDB():

    # command
    command = """
    CREATE TABLE IF NOT EXISTS books (
        idn VARCHAR(10), 
        isbn VARCHAR(17), 
        title VARCHAR(128)
    );"""

    executeCommand(command)

def executeCommand(command):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    # execute
    cursor.execute(command)
    connection.commit()

    # close
    connection.close()

def storeBook(idn, isdn, title):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    command = "INSERT INTO books VALUES (?, ?, ?)"
    cursor.execute(command, (idn, isdn, title))

    # close
    connection.commit()
    connection.close()