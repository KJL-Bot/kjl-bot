#!/usr/bin/env python3

import mariaDatabase
import mariadb
import config

tsvFilename = "verlage-von-google-sheet.tsv"



def importTSV(filename):

    with open(filename, 'r') as f:
        content = f.read()

        # split into lines
        lines = content.split('\n')

        # go through each line, skipping the header line
        for line in lines[1:]:

            # split into fields
            fields = line.split('\t')

            # extract fields
            name = fields[0].strip()
            webUrl = fields[1].strip()
            twitterUrl = fields[2].strip()
            jlpNominated = fields[3].strip()
            jlpAwarded = fields[4].strip()
            kimiAwarded = fields[5].strip()

            # mappings
            if twitterUrl == '?' or len(twitterUrl) == 0:
                twitterUrl = None

            jlpNominated = convertText2Boolean(jlpNominated)
            jlpAwarded = convertText2Boolean(jlpAwarded)
            kimiAwarded = convertText2Boolean(kimiAwarded)

            # xtore in DB
            #print(f"{name}\t{webUrl}\t{twitterUrl}\t{jlpNominated}\t{jlpAwarded}\t{kimiAwarded}")
            storePublisher(name, webUrl, twitterUrl, jlpNominated, jlpAwarded, kimiAwarded)

def convertText2Boolean(text):
    if text == 'ja':
        return True

    if text == 'nein':
        return False

    # default: None
    return None


def createPublishersTable():

    tableName = config.relevantPublishersTableName

    # Create books table
    command = f"""
    CREATE TABLE IF NOT EXISTS {tableName} (
        id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(128) UNIQUE NOT NULL,
        webUrl VARCHAR(128),
        twitterUrl VARCHAR(128),
        jlpNominated BOOL,
        jlpAwarded BOOL,
        kimiAwarded BOOL
    );"""

    mariaDatabase.executeCommand(command)

def storePublisher(name, webUrl, twitterUrl, jlpNominated, jlpAwarded, kimiAwarded):

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    tableName = config.relevantPublishersTableName

    command = f"INSERT INTO {tableName} (name, webUrl, twitterUrl, \
        jlpNominated, jlpAwarded, kimiAwarded) \
        VALUES (?, ?, ?, ?, ?, ?)"

    try:

        cursor.execute(command, \
            (name, webUrl, twitterUrl, \
            jlpNominated,jlpAwarded, jlpNominated)
        )

        print(f"Added new publisher: {name}")

    # ignore feedback on violation of UNIQUE contraint
    except mariadb.IntegrityError:
        print(f"Publisher already in database: {name}")
        pass

    except Exception as e:
        print(e)

    # close
    connection.commit()
    connection.close()

def findPublisherDetailsWithName(cursor, publisherName):

    # replace double quotes by single quotes
    publisherName = publisherName.replace('"', "'")

    tableName = config.relevantPublishersTableName

    command = f"""SELECT id, jlpNominated, jlpAwarded, kimiAwarded FROM {tableName} WHERE name LIKE "%{publisherName}%" """
    cursor.execute(command)
    publishers = cursor.fetchall()

    if len(publishers) == 0:
        return None

    if len(publishers) >= 1:
        (id, jlpNominated, jlpAwarded, kimiAwarded) = publishers[0]
        return (id, jlpNominated, jlpAwarded, kimiAwarded)

def getAwardsForPublisherWithID(cursor, publisherId):

    # prepare results
    jplNominated = 0
    jplAwarded = 0
    kimiAwarded = 0

    tableName = config.relevantPublishersTableName

    command = f"SELECT jlpNominated, jlpAwarded, kimiAwarded FROM {tableName} WHERE id = ?"
    cursor.execute(command, (publisherId,))
    publishers = cursor.fetchall()

    # replace default results with results from database
    if len(publishers) >= 0:
        (jlpNominated, jlpAwarded, kimiAwarded) = publishers[0]

    return (jlpNominated, jlpAwarded, kimiAwarded)



def matchBooksToPublishers():

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    booksTableName = config.booksTableName

    # get all books from DB
    command = f"SELECT idn, publisher FROM {booksTableName} ORDER BY addedToSql DESC"
    cursor.execute(command)
    books = cursor.fetchall()

    # go through each book
    counter = 0
    for (idn, publisherName) in books:

        # skip if we have no publisher name
        if publisherName is None:
            continue

        # do we find the publisher in our relevantPublisher table?
        publisherDetails = findPublisherDetailsWithName(cursor, publisherName)

        # if we have a match
        if publisherDetails is not None:

            # unpack details
            (publisherId, publisherJLPNominated, publisherJLPAwarded, publisherKimiAwarded) = publisherDetails

            # print(f"Found a relevant publisher: {publisherName} -> {publisherId}")

            # update books table with relevantPublisher and awards
            command = f"UPDATE {booksTableName} SET matchesRelevantPublisher = ?, publisherJLPNominated = ?, publisherJLPAwarded = ?, publisherKimiAwarded = ? WHERE idn = ?"
            try:
                cursor.execute(command, (publisherId, publisherJLPNominated, publisherJLPAwarded, publisherKimiAwarded, idn))
            except Exception as e:
                print(e)

            connection.commit()

    connection.close()

if __name__ == '__main__':

    # create table
    createPublishersTable()

    # import data
    importTSV(tsvFilename)

    # test matching of publisher name
    publisherName = "FISCHER"
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()
    publisherId = findPublisherIDWithName(cursor, publisherName)
    print(f"The publisher {publisherName} has the ID {publisherId}.")
    connection.close()

    # whatch whole database to relevant publishers
    matchBooksToPublishers()
