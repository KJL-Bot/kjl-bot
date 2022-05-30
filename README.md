# kjl-bot
Eine Zusammenstellung von Python scripts, die Daten für den  'Kinder- und Jugendliteratur' Bot erzeugen.

## Hardware
Ein Raspberry PI 4 ist auf meinem Dachboden installiert (siehe Foto) und über Ethernet mit meiner Fritz!Box verbunden. 
Er läuft 24h durch und ist, wenn bei mir nicht die Sicherungen durch Unwetter rausfliegen, stabil verfügbar. 

Allerdings nutze ich, wie ihr unten sehen werdet, meine Domain zum Hosten des RSS Feeds. 

![image](https://user-images.githubusercontent.com/5444043/165967008-659881ed-c7e9-4f08-a0b7-97906db142cb.jpeg)

Hier handelt sich aber nur um einen über FTP erreichbaren Webserver, der natürlich erheblich billiger ist als ein kommerzieller Server, der Skripte ausführen kann.

## Software
Die Skripte werden alle 15 Minuten automatisch über einen cron job aufgerufen. Einstiegspunkt ist `scrape.sh`.

## Was machen die Skripte?
### Diagram
<img width="800" alt="image" src="https://user-images.githubusercontent.com/5444043/165967473-2c85368d-04ae-4185-b2b2-99ffc8a0eda2.png">


### Beschreibung

#### 1. Abfrage der DNB
Bei jedem Aufruf wird die DNB Datenbank nach den neuesten Jugendbüchern befragt, sortiert nach ID-Nummer der DNB (IDN). 
Dabei nehme ich an, dass höhere IDNs neueren Einträgen entsprechen.

Folgender CQL-Query wird verwendet:

```
sgt=K and jhr<2023 and jhr>2020 and spr=ger and mat=books sortBy idn/sort.descending
```


| sgt=K | Suche über alle Sachgruppen nach Kinder- und Jugendbuchliteratur |
| jhr | Erscheinungsjahr |
| spr | Sprache |
| mat | Materialart |
| sortBy | idn/sort.descending | Sortierung nach IDN, höchste zuerst |


**Tipp:** Dieser Query kann auch direkt in die [Eingabemaske](https://portal.dnb.de/opac.htm) der DNB Datenbank eingegeben werden → dabei ‘Expertensuche’ anklicken. 
Alternativ einfach [diese URL](https://portal.dnb.de/opac/simpleSearch?query=sgt%3DK+and+jhr%3C2023+and+jhr%3E2020+and+spr%3Dger+and+mat%3Dbooks+sortBy+idn%2Fsort.descending&cqlMode=true) aufrufen.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/5444043/165969064-9a1c727a-82b7-4dd6-9951-5baac52b8ea2.png">

#### 2. Speicherung in sqlite Datenbank
Die Ergebnisse werden in einer lokalen sqlite Datenbank auf dem Raspberry Pi gespeichert. 
Duplikate werden aussortiert, das heisst, dass nur Einträge mit einer noch nicht bekannten IDN gespeichert werden. 
Aktualisierungen von Metadaten werden zur Zeit nicht überprüft.

#### 3. Zeitstempel
Jeder neue Eintrag bekommt einen aktuellen Zeitstempel. Zusätzlich speichert die Datenbank, wann die DNB Datenbank das letzte Mal abgefragt wurde.

#### 4. RSS-Feed
Die Skripte erzeugen einen RSS Feed. Jeder Eintrag enthält dabei eine Liste von Büchern, die bei einer DNB-Abfrage neu hinzugekommen sind. Die XML-Datei, die die Daten für den RSS-Feed speichert, wird per FTP auf den Webserver übertragen, und ist unter der URL http://www.artisticengines.com/kjl/kjlbot.xml abgreifbar.

#### 5. JSON-Feed
Die jüngst erschienenen Bücher werden im JSON format as der Datenbank exportiert. Die Datei wirden ebenfalls per FTP auf den Webserver übertragen und ist dort unter der URL http://artisticengines.com/kjl/recentBooks.json abgreifbar.

## Wie lässt sich der RSS Feed lesen?
Dieser RSS Feed kann mit jedem RSS Reader dargestellt werden, ich empfehle [NetNewsWire](https://netnewswire.com), der kostenlos ist und für den Mac und iOS zu haben ist.

## Format der exportierten JSON Datei
```
[
  {
    "idn": "1258732912",
    "title": "Different kinds of Love",
    "subTitle": "Zweite Chance für die LIebe",
    "titleAuthor": "Svenja Bartsch",
    "publicationPlace": "Norderstedt",
    "publisher": "BoD – Books on Demand",
    "publicationYear": "2022",
    "projectedPublicationDate": "2022-05-01",
    "linkToDataset": "https://d-nb.info/1258732912",
    "isbnWithDashes": "978-3-7562-0090-0",
    "addedToSql": "2022-05-30T09:45:05Z",
    "coverUrl": "https://portal.dnb.de/opac/mvb/cover?isbn=978-3-7562-0090-0&size=l"
  },
  {
    "idn": "1258732866",
    "title": "Entchen Annabell/Entchen Annabell auf Schatzsuche",
    "subTitle": "Fünf tierische Freunde erleben ein Abenteuer",
    "titleAuthor": "M. Markus Ermer",
    "publicationPlace": "Berlin",
    "publisher": "epubli",
    "publicationYear": "2022",
    "projectedPublicationDate": "2022-05-01",
    "linkToDataset": "https://d-nb.info/1258732866",
    "isbnWithDashes": "978-3-7565-0187-8",
    "addedToSql": "2022-05-30T09:45:05Z",
    "coverUrl": "https://portal.dnb.de/opac/mvb/cover?isbn=978-3-7565-0187-8&size=l"
  },
  ...
]

