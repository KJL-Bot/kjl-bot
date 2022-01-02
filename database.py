import sqlite3
from datetime import datetime

databaseName = "kjl.db"

def createDB():

    # command
    command = """
    CREATE TABLE IF NOT EXISTS books (
        idn VARCHAR(10) PRIMARY KEY, 
        isbn VARCHAR(17), 
        dateAdded DATE,
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



def storeBook(book):

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    dateAdded = datetime.utcnow()

    command = "INSERT INTO books (dateAdded, idn, isbn, title) VALUES (?, ?, ?, ?)"
    
    try:
        cursor.execute(command, (dateAdded, book.idn, book.isbns[0].withDashes, book.title))
        print(f"Adding new book. Title: {book.title}")
    except:
        pass

    # close
    connection.commit()
    connection.close()

def displayBookContent():

    # connect    
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()   

    command = "SELECT * FROM books ORDER BY dateAdded DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    for book in books:
        print(book)
    

    connection.close()
