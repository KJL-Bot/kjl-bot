#!/usr/bin/env python3

import mariaDatabase
import mariadb
import config
import logbookManager
from datetime import datetime
import string

def createReviewsTable():

    # Create books table
    command = f"CREATE OR REPLACE TABLE {config.reviewsTableName} ( \
        id INT AUTO_INCREMENT primary key, \
        matchingBookIdn VARCHAR(10), \
        excludeReview BOOL DEFAULT False, \
        addedToSql TIMESTAMP, \
        published TIMESTAMP, \
        scraper VARCHAR(128), \
        reviewSite VARCHAR(128), \
        isbnWithDashes VARCHAR(20), \
        author VARCHAR(256), \
        title VARCHAR(256), \
        url VARCHAR(1024) UNIQUE, \
        INDEX(url) \
    );"

    mariaDatabase.executeCommand(command)


def addReview(published, scraper, reviewSite, author, title, isbnWithDashes, url):

    command = f"INSERT INTO {config.reviewsTableName} SET \
            published = '{published}', \
            scraper = '{scraper}', \
            reviewSite = '{reviewSite}', \
            author = '{author}', \
            title = '{title}', \
            isbnWithDashes = '{isbnWithDashes}',\
            url = '{url}'"

    # connect
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # try inserting new book
    try:
        cursor.execute(command)

    # ignore feedback on violation of UNIQUE contraint
    except mariadb.IntegrityError:
        pass

    # other errors
    except Exception as e:
        print(f"{type(e).__name__} was raised with error number: {e}")
        logbookManager.logMessage(relatesToIDN=None, description=f"storeReview: {type(e).__name__} was raised with error number: {e}")
        print("Error while storing review:")
        print(f"{author}: {title}")
        pass


    # close
    connection.commit()
    connection.close()

# goes through each unmatched rewview and matched iit to the most likely book
def matchReviews():

    # connect to DB
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # get all reviews without matched idn from reivews table
    command = f"SELECT id, isbnWithDashes, author, title FROM {config.reviewsTableName} WHERE matchingBookIdn IS NULL"
    cursor.execute(command)
    reviews = cursor.fetchall()

    # go through each review
    for (reviewId, isbnWithDashes, author, title) in reviews:
        print(f"\n{author}: {title}")

        # convert author into tokens
        authorTokenList = author.replace(',', '').split()
        authorTokens = ','.join(authorTokenList)

        # convert title into tokens
        titleTokenList = title.replace(',', '').split()
        titleTokens = ','.join(titleTokenList)

        # match command
        command = f"SELECT idn, sortingAuthor, title FROM {config.booksTableName} WHERE MATCH(sortingAuthor) AGAINST('{authorTokens}') \
            AND MATCH(title) AGAINST('{titleTokens}')"
        # print(command)
        cursor.execute(command)
        matchedBook = cursor.fetchone()

        # the most likely match is the first returned result
        (matchedIdn, matchedAuthor, matchedTitle) = matchedBook
        print(f"Match: {matchedIdn} -> {matchedAuthor}: {matchedTitle}")

        # update the review accordingly
        updateReview(reviewId, matchedIdn)

    connection.close()

# updates review table to relate review to a book
def updateReview(reviewId, bookIdn):

    # connect to DB
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    command = f"UPDATE {config.reviewsTableName} SET matchingBookIdn = '{bookIdn}' WHERE id={reviewId}"
    cursor.execute(command)

    connection.commit()
    connection.close()

# gets relevant reviews and returns them as an array of tuples (matchingBookIdn, reviewSite, url)
def getReviews(cursor):
        # get all available matched reviews that are marked not to be excluded
        command = f"SELECT matchingBookIdn, reviewSite, url FROM {config.reviewsTableName} WHERE matchingBookIdn IS NOT NULL AND excludeReview=0"
        cursor.execute(command)
        reviewResult = cursor.fetchall()

        # transfer to local array
        reviews = []
        for (matchingBookIdn, reviewSite, url) in reviewResult:
            reviews.append((matchingBookIdn, reviewSite, url))

        return reviews

# finds the bookReviews that match the given bookIdn. Returns an array of matching reviews with tuples (reviewSite, url)
def matchingReviewsForIdn(bookIdn, availableReviews):

    matchingReviews = []

    for (matchingBookIdn, reviewSite, url) in availableReviews:
        if bookIdn == matchingBookIdn:
            matchingReview = (reviewSite, url)
            matchingReviews.append(matchingReview)

    # we get here if no match took place
    return matchingReviews

    
# def matchReviewsOld():
#     # connect to DB
#     connection = mariaDatabase.getDatabaseConnection()
#     cursor = connection.cursor()
#
#     # get all reviews without matched idn from reivews table
#     command = f"SELECT id, isbnWithDashes, author, title FROM {config.reviewsTableName} WHERE matchingBookIdn IS NULL"
#     cursor.execute(command)
#     reviews = cursor.fetchall()
#
#     # go through each review
#     for (reviewId, isbnWithDashes, author, title) in reviews:
#         print(f"\n{author}: {title}")
#
#         # match title
#         command = f"SELECT idn, sortingAuthor FROM {config.booksTableName} WHERE title LIKE '%{title}%'"
#         cursor.execute(command)
#         matchedBooks = cursor.fetchall()
#         for bookIdn, sortingAuthor in matchedBooks:
#             if fuzzyNameMatch(author, sortingAuthor) == True:
#                 print(f"Match: {bookIdn} -> {sortingAuthor}: {title}")
#
#                 # update review table
#                 updateReview(reviewId, bookIdn)
#
#
#     # close
#     #connection.commit()
#     connection.close()
#
# def fuzzyNameMatch(author, author2):
#
#     # extract author first nad last names into a set
#     authorWords1 = set([word.strip(string.punctuation) for word in author.split()])
#     authorWords2 = set([word.strip(string.punctuation) for word in author2.split()])
#
#     #print(f"set1: {authorWords1}")
#     #print(f"set2: {authorWords2}")
#
#     numberOfCommonWords = len(authorWords1.intersection(authorWords2))
#
#     # return True if at least one of the words match
#     return numberOfCommonWords > 0

if __name__ == '__main__':

    # remove old table an replace with new and empty one
    #createReviewsTable()

    # addReview(
    #     published = datetime.now(),
    #     scraper = "fazScraper",
    #     reviewSite = "FAZ",
    #     author = "Andy Giefer",
    #     title = "My favroute things",
    #     isbnWithDashes = "978-3-95470-276-3",
    #     url="https://www.apple.com"
    # )

    matchReviews()
