from feedgen.feed import FeedGenerator
import config
from datetime import datetime
import pytz
from pathlib import Path


class rssEntry:

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

    for rssEntry in rssEntries:

        # localize publcation date
        localizedPublicationDate = timezone.localize(rssEntry.publicationDate)
   
        fe = fg.add_entry()
        fe.id(rssEntry.id)
        fe.title(rssEntry.title)
        fe.content(rssEntry.content, type='CDATA')
        fe.published(localizedPublicationDate)

    fg.rss_file(config.rssFeedFilename, pretty=True) # Write the RSS feed to a file

    return Path(config.rssFeedFilename)

if __name__ == '__main__':

    generateFeed()


