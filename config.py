dnbSearchQuery = "sgt=K and jhr<2023 and jhr>2020 and spr=ger and mat=books sortBy idn/sort.descending"
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

numberOfRetrievedRecords = 50
maximumNumberOfRSSEntries = 10

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

# Artistic Engines FTP
ftpServer = 'ftp.artisticengines.com'
ftpTargetFolder = 'kjl/'

# KJL Server FTP-SSL
kjlFtpSSLHostName = "kjl-bot.de"
kjlFtpSSLPort = 21
kjlFtpSSLTargetDir = "web/wp-content/uploads/kjl-data"
