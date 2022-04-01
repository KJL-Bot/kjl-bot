dnbSearchQuery = "sgt=K and jhr<2023 and jhr>2020 and spr=ger and mat=books sortBy idn/sort.descending"
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

ftpServer = 'ftp.artisticengines.com'
ftpTargetFolder = 'kjl/'

