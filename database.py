import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid
import rssFeed
import html

databaseName = "kjl.db"


#### General

def createDB():

    createBooksTable()
    createLogbook()

def executeCommand(command):

    # connect
    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()

    # execute
    cursor.execute(command)
    connection.commit()

    # close
    connection.close()
