# kjl-bot
Eine Zusammenstellung von Python-Scripts, die Daten für den  'Kinder- und Jugendliteratur' Bot erzeugen.

## Hardware
Ein Raspberry PI 4 läuft 24h durch, damit ist es möglich, die Schnittstelle der Deutschen Nationalbibliothek im Stundenrhythmus abzufragen.

Ein Auszug der Datenbank im gleichen Rhythmus via SFTP auf den Server kjl-bot.de exportiert. Auf diese Weise können die Kosten niedrig gehalten werden, da der kommerzielle Server lediglich die Daten via Wordpress zur Verfügung stellen muss. Das Scrapen erfolgt auf dem Raspberry Pi.

![image](https://user-images.githubusercontent.com/5444043/165967008-659881ed-c7e9-4f08-a0b7-97906db142cb.jpeg)

## Software
Die Skripte werden alle 60 Minuten automatisch über einen cron job aufgerufen. Einstiegspunkt ist `scrape.sh`.

## Was machen die Skripte?
### Diagram

```mermaid
  flowchart LR
    dnb((DNB))
    scraper(Scraper)
    cronjob(Cron Job ever 60 minutes)
    database([Database])
    matchBooksToPublishers(Match books to publishers)
    identifyRelevantBooks(Identify relevant books)
    rssFeedCreator(RSS Feed Creator)
    rssFeed{{RSS Feed}}
    RSSUploader(RSS Uploader)
    artisticEngines(artisticEngines.com)
    
    jsonFeedCreator(JSON Feed Creator)
    jsonFeed{{JSON Feed}}
    jsonUploader(JSON Uploader)
    kjl-bot(kjl-bot.de)
    
    dnb-->scraper-->database-->matchBooksToPublishers-->identifyRelevantBooks-->rssFeedCreator--->rssFeed-->RSSUploader-->artisticEngines
    cronjob-->scraper
    identifyRelevantBooks-->jsonFeedCreator-->jsonFeed-->jsonUploader-->kjl-bot
    jsonUploader-->artisticEngines
 ```

### Beschreibung

#### 1. Abfrage der DNB
Bei jedem Aufruf wird die DNB Datenbank nach den neuesten Jugendbüchern befragt, sortiert nach ID-Nummer der DNB (IDN). 
Dabei nehme ich an, dass höhere IDNs neueren Einträgen entsprechen.

Folgender CQL-Query wird verwendet:

```
sgt=K and jhr<2023 and jhr>2020 and spr=ger and mat=books sortBy idn/sort.descending
```

| Feld  | Beschreibung |
| ------------- | ------------- |
| `sgt=K` | Suche über alle Sachgruppen nach Kinder- und Jugendbuchliteratur |
| `jhr` | Erscheinungsjahr |
| `spr` | Sprache |
| `mat` | Materialart |
| `sortBy idn/sort.descending` | Sortierung nach IDN, höchste zuerst |


**Tipp:** Dieser Query kann auch direkt in die [Eingabemaske](https://portal.dnb.de/opac.htm) der DNB Datenbank eingegeben werden → dabei ‘Expertensuche’ anklicken. 
Alternativ einfach [diese URL](https://portal.dnb.de/opac/simpleSearch?query=sgt%3DK+and+jhr%3C2023+and+jhr%3E2020+and+spr%3Dger+and+mat%3Dbooks+sortBy+idn%2Fsort.descending&cqlMode=true) aufrufen.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/5444043/165969064-9a1c727a-82b7-4dd6-9951-5baac52b8ea2.png">

#### 2. Speicherung in einer MariaDB Datenbank
Die Ergebnisse werden in einer lokalen MariaDB Datenbank auf dem Raspberry Pi gespeichert. 
Duplikate werden aussortiert, das heisst, dass nur Einträge mit einer noch nicht bekannten IDN gespeichert werden. 

#### 3. Zeitstempel
Jeder neue Eintrag bekommt einen aktuellen Zeitstempel. Zusätzlich speichert die Datenbank, wann die DNB Datenbank das letzte Mal abgefragt wurde.

#### 4. RSS-Feed
Die Skripte erzeugen einen RSS Feed. Jeder Eintrag enthält dabei eine Liste von Büchern, die bei einer DNB-Abfrage neu hinzugekommen sind. Die XML-Datei, die die Daten für den RSS-Feed speichert, wird per FTP auf den Webserver übertragen, und ist unter der URL [https://www.artisticengines.com/kjl/kjlbot.xml](https://www.artisticengines.com/kjl/kjlbot.xml) abgreifbar.

#### 5. JSON-Feed
Die jüngst erschienenen Bücher werden im JSON format as der Datenbank exportiert. Die Datei wirden ebenfalls per FTP auf den Webserver übertragen und ist dort unter der URL [https://artisticengines.com/kjl/recentBooks.json](https://artisticengines.com/kjl/recentBooks.json) abgreifbar. Alternativ stehen die Daten auf dem kjl-bot.de Server, bereit, und zwar unter [https://kjl-bot.de/wp-content/uploads/kjl-data/recentBooks.json](https://kjl-bot.de/wp-content/uploads/kjl-data/recentBooks.json)

## Wie lässt sich der RSS Feed lesen?
Dieser RSS Feed kann mit jedem RSS Reader dargestellt werden, ich empfehle [NetNewsWire](https://netnewswire.com), der kostenlos ist und für den Mac und iOS zu haben ist.

## Format der exportierten JSON Datei
```
[
  {
    "idn": "1247559262",
    "title": "GEOlino mini Sonderheft 1/2021 - Freundschaft",
    "sortingTitle": "geolino mini sonderheft 1/2021 - freundschaft",
    "titleAuthor": "Rosa Wetscher",
    "authorName": "Wetscher, Rosa",
    "secondaryAuthorName": "Wetscher, Rosa",
    "sortingAuthor": "Wetscher, Rosa",
    "keywords": "",
    "publicationPlace": "Hamburg",
    "publisher": "Gruner + Jahr",
    "publicationYear": "2022",
    "projectedPublicationDate": "2022-05-01",
    "linkToDataset": "https://d-nb.info/1247559262",
    "isbnWithDashes": "978-3-652-01245-4",
    "addedToSql": "2023-02-02T09:16:06Z",
    "publisherJLPNominated": 0,
    "publisherJLPAwarded": 0,
    "publisherKimiAwarded": 0,
    "coverUrl": "https://portal.dnb.de/opac/mvb/cover?isbn=978-3-652-01245-4&size=l"
  },
  {
    "idn": "1278999248",
    "title": "Freddi",
    "sortingTitle": "freddi",
    "subTitle": "Die kleine graue Maus aus Hellevoetsluis",
    "titleAuthor": "Emilie Francuz, Danny Tobias Francuz",
    "authorName": "Francuz, Emilie",
    "secondaryAuthorName": "Francuz, Danny Tobias",
    "sortingAuthor": "Francuz, Emilie",
    "keywords": "",
    "publicationPlace": "Norderstedt",
    "publisher": "BoD â€“ Books on Demand",
    "publicationYear": "2023",
    "projectedPublicationDate": "2023-01-01",
    "linkToDataset": "https://d-nb.info/1278999248",
    "isbnWithDashes": "978-3-7568-5249-9",
    "addedToSql": "2023-02-02T04:05:04Z",
    "publisherJLPNominated": 0,
    "publisherJLPAwarded": 0,
    "publisherKimiAwarded": 0,
    "coverUrl": "https://portal.dnb.de/opac/mvb/cover?isbn=978-3-7568-5249-9&size=l"
  },
  ...
]

