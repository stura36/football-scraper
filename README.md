## Short description

### player_scrapers.py

Consists of two classes: PlayerScraper and Extractor<br>
PlayerScraper loads the urls from a csv file and for each url it scrapes the relevant information.<br>
The other class Extractor is where for each feature there is a corresponding method that define the logic for extracting the relevant information from a webpage<br>

### database_setup.py

Creates a connection to the database and sets up the players and players_log tables<br>

### database_load.py

Loads the data from a csv file into the database<br>

### queries.py

Runs queries on the database<br>

## Instructions

Python 3.11.4<br>
PostgreSQL 16

Create virtual environment<br>
Activate virtual environment<br>
Install dependencies to virtual environment using requirements.txt<br>

```
pip install -r requirements.txt
```

Create a .env file with information for connecting to a database<br>
Content of .env file should be formatted in a following way:

```
DB_HOST=xxxxx
DB_USER=xxxxx
DB_PASS=xxxxx
DB_PORT=xxxxx
DB_NAME=xxxxx
```

Setup database tables by running:<br>

```
python database_setup.py
```

Load existing data(playersData.csv) by running pass the filepath as command line argument:<br>

```
python database_load.py path_to_playersDatacsv
```

Run web scraper by passing the filepath to the urls.csv file as command line argument:<br>

```
python player_scrapers.py <path_to_urls>
```

Run database_load.py to load the scraped data into the database by passing the filepath to the players_scraped.csv file as command line argument:

```
python database_load.py players_scraped.csv
```

<br>

Run queries by passing the club name as command line argument:

```
python queries.py "<club name>"
```
