# Return the URL of the book cover for given IBDN and size ('s', 'm', 'l')
def coverUrl(isbnWithDashes, size):

    url = f"https://portal.dnb.de/opac/mvb/cover?isbn={isbnWithDashes}&size={size}"
    return url
