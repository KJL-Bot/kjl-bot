from feedgen.feed import FeedGenerator
import config
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from dateutil.relativedelta import relativedelta
import mariaDatabase



class RSSEntry:

    def __init__(self, id, publicationDate, title, content):
        self.id = id
        self.publicationDate = publicationDate
        self.title = title
        self.content = content

    def __str__(self):

        description = ""
        description += f"id: {self.id}\n"
        description += f"publicationDate {self.publicationDate}\n"
        description +=f"title: {self.title}\n"
        description += f"content:\n"
        description += self.content

        return description

def generateRSSEntries():

    # result are stored here
    rssEntries = []

    # the first day of the month following  this month (eg. March if we are in Februray)
    now = datetime.utcnow()
    firstDayOfNextMonth = now.replace(day=1) + relativedelta(months=1)

    # connect
    # connection = mariadb.connect(databaseName, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    connection = mariaDatabase.getDatabaseConnection()
    cursor = connection.cursor()

    # get logbook entries
    command = "SELECT timestamp, id, description  FROM logbook ORDER BY timestamp DESC"
    cursor.execute(command)
    logbookEntries = cursor.fetchall()

    # go through each entry
    for logbookEntry in logbookEntries:

        (logBookTimestamp, logBookId, logBookDescription) = logbookEntry

        command = "SELECT idn, isbnWithDashes, title, subTitle, titleAuthor, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset, matchesRelevantPublisher " +\
            "FROM books WHERE logbookMessageId = ? ORDER BY idn DESC"


        try:
            cursor.execute(command, (logBookId, ))
            books = cursor.fetchall()

            # contains the the data for all the books appearing in the currenty rss entry
            entryLines = []

            # count the number of valid books
            bookCounter = 0

            for (idn, isbnWithDashes, title, subTitle, titleAuthor, publicationPlace, publisher, publicationYear, projectedPublicationDate, addedToSql, linkToDataset, matchesRelevantPublisher) in books:

                # skip entries without ISDN
                if isbnWithDashes is None:
                    continue

                # skip entries without expected publication date
                if projectedPublicationDate is None:
                    continue

                # skip entries whose projected publication date is too far in the future
                if projectedPublicationDate > firstDayOfNextMonth:
                    continue

                # here we know that the book is a valid entry. So we can count it
                bookCounter += 1

                # start the entry with the title
                entryLines.append(f"<b>{title}</b>")

                # skip subtitle if not present
                if subTitle is not None:
                    entryLines.append(f"<i>{subTitle}</i>")

                # skip author if not present
                if titleAuthor is not None:
                    entryLines.append(f"Von {titleAuthor}")

                # add publicationPlace, publisher, publicationYear
                entryLines.append(f"{publicationPlace}: {publisher}, {publicationYear}")

                # skip projectedPublicationDate if not present
                if projectedPublicationDate is not None:
                    entryLines.append(f"Erwartete Publikation laut DNB: {projectedPublicationDate.strftime('%Y-%m')}")

                # add DNB link
                entryLines.append(f"DNB Link: <a href=\"{linkToDataset}\">{linkToDataset}</a>")

                # skip isbn if not present
                if isbnWithDashes is not None:
                    entryLines.append(f"ISBN: {isbnWithDashes}")

                if matchesRelevantPublisher is not None:
                    entryLines.append(f"Relevanter Verlag identifiziert: Datenbank ID {matchesRelevantPublisher}")
                else:
                    entryLines.append(f"Dieser Verlag is laut Datenbank nicht relevant.")

                # empty line at the end
                entryLines.append(f"")

            # now, we know how many books we have. skip to next entry if there are no valid books to list in the current entry
            if bookCounter == 0:
                continue


            # Derive entry title and introductory text
            entryTitle = f"{bookCounter} neue Bücher in DNB Datenbank"
            introText = f"Die folgenden {bookCounter} Bücher wurden zur DNB hinzugefügt."

            if bookCounter == 1:
                entryTitle = f"Ein neues Buch in DNB Datenbank"
                introText = f"Das folgende Buch wurde zur DNB hinzugefügt."

            # add introtext at the beginning of the entry, followed by an empty line
            entryLines.insert(0, introText)
            entryLines.insert(1, "")

            # wrap lines in HTML paragraphs
            for lineIndex in range(0, len(entryLines)):
                entryLine = entryLines[lineIndex]
                wrappedEntryLine = f"{entryLine}<br>"
                entryLines[lineIndex] = wrappedEntryLine

            # Convert lines into string
            rssContent = '\n'.join(entryLines)

            # create new entry
            entry = RSSEntry(id = str(logBookId), publicationDate = logBookTimestamp, title = entryTitle, content = rssContent)

            # append to array of other entries
            rssEntries.append(entry)



        except Exception as e:
            print(f"Fehler beim suchen der Bücher für logbook Entry mit id {logBookId}.")
            print(e)


    connection.close()

    return rssEntries

def generateFeed(rssEntries):

    fg = FeedGenerator()
    fg.id(config.rssFeedId)
    fg.title(config.rssFeedTitle)
    fg.author(config.rssFeedAuthor)
    fg.link( href=config.rssAlternateLink, rel='alternate' )
    fg.logo(config.rssFeedLogo)
    fg.subtitle(config.rssFeedSubtitle)
    fg.link( href=config.rssFeedUrl, rel='self' )
    fg.language(config.rssFeedLanguage)

    timezone = pytz.utc

    entryCounter = 0

    for rssEntry in rssEntries:

        # localize publcation date
        localizedPublicationDate = timezone.localize(rssEntry.publicationDate)

        fe = fg.add_entry()
        fe.id(rssEntry.id)
        fe.title(rssEntry.title)
        fe.content(rssEntry.content, type='CDATA')
        fe.published(localizedPublicationDate)

        # exit loop when the maximum number of rssEntries is reached
        entryCounter += 1
        if entryCounter >= config.maximumNumberOfRSSEntries:
            break

    fg.rss_file(config.rssFeedFilename, pretty=True) # Write the RSS feed to a file

    return Path(config.rssFeedFilename)

if __name__ == '__main__':
    rssEntries = generateRSSEntries()
    generateFeed()
