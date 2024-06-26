#dnbSearchQuery = "sgt=K and jhr>=2020 and jhr<2023 and spr=ger and mat=books sortBy idn/sort.descending"
#dnbSearchQuery = "idn=1250917204"
#dnbSearchQuery = 'tit=Klimawandel and location=onlinefree'
#dnbSearchQuery = "mat=books sortBy idn/sort.descending"

databaseName = "kjl"
databaseUser="kjl"
databasePassword="i232kAWLF."
databaseHost="localhost"

booksTableName = "books"
logbookTableName = "logbook"
relevantPublishersTableName = "relevantPublishers"
reviewsTableName = "reviews"

numberOfYearsToScrape = 2
numberOfRetrievedRecords = 30000
maximumNumberOfRSSEntries = 10
maximumNumberOfJSONEntries = 30000

rssFeedId = 'com.artisticengines.kjlbot'
rssFeedTitle = 'KJL Bot'
rssFeedSubtitle = "Ein Tracker für Neuerscheinungen im Bereich der Kind- und Jugendbücher."
rssFeedAuthor = {'name':'KJL Bot','email':'kjl@artisticengines.com'}
rssAlternateLink = 'http://artisticengines.com/kjl/index.html'
rssFeedLogo = 'http://artisticengines.com/kjl/rssFeedLogo.jpg'
rssFeedFilename = 'kjlbot.xml'
rssFeedUrl = f'http://artisticengines.com/kjl/{rssFeedFilename}'
rssFeedLanguage = 'de'

recentBooksJsonFileName = "recentBooks.json"
jsonFeedUrl = f'http://artisticengines.com/kjl/{recentBooksJsonFileName}'

# logBook: the id of this command is used to group imported booked together, as they are imported together, associated with the same logbookId
scrapeForYearCommand = "scrapeForYear"

# Artistic Engines FTP
aeFtpServer = 'ftp.artisticengines.com'
aeFtpTargetFolder = 'kjl/'
aeFtpSSLPort = 21

# Artistic Engines Server FTP-SSL
#aeFtpSSLHostName = "ftp.artisticengines.com"
#aeFtpSSLPort = 21
#aeFtpSSLTargetDir = "kjl/"

# KJL Server FTP-SSL
kjlFtpSSLHostName = "kjl-bot.de"
kjlFtpSSLPort = 21
kjlFtpSSLTargetDir = "web/wp-content/uploads/kjl-data"
