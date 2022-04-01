#!/usr/bin/python 
import mariadb
import publishers 
import config

def mariaExample():

    conn = mariadb.connect(
        user="kjl",
        password="i232kAWLF.",
        host="localhost",
        database="test")
    cur = conn.cursor() 

    #retrieving information 
    some_name = "Georgi" 
    cur.execute("SELECT first_name,last_name FROM employees WHERE first_name=?", (some_name,)) 

    for first_name, last_name in cur: 
        print(f"First name: {first_name}, Last name: {last_name}")
        
    #insert information 
    try: 
        cur.execute("INSERT INTO employees (first_name,last_name) VALUES (?, ?)", ("Maria","DB")) 
    except mariadb.Error as e: 
        print(f"Error: {e}")

    conn.commit() 
    print(f"Last Inserted ID: {cur.lastrowid}")
        
    conn.close()



#### General

def getDatabaseConnection():
    
    # connect    
    connection = mariadb.connect(
        user=config.databaseUser,
        password=config.databasePassword,
        host=config.databaseHost,
        database=config.databaseName)

    return connection

def executeCommand(command):

    # connect    
    connection = getDatabaseConnection()
    cursor = connection.cursor()  

    # execute
    cursor.execute(command)
    connection.commit()

    # close
    connection.close()




if __name__ == '__main__':
    # createDB()

    rssEntries = generateRSSEntries()