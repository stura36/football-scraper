## Short description

### player_scrapers.py

Consists of two classes: PlayerScraper and Extractor<br>
+ PlayerScraper
  - Loads the urls from a csv file and for each url scrapes the relevant information using Extractor class
+ Extractor
  - For each feature defines the logic for extracting data from the webpage
### database_setup.py

Creates a connection to the database and sets up the players and players_log tables<br>
+ players
  - holds all player information
  - (Full name, Date of birth) combination and uuid define each unique row
+ players_log
  - holds last player_update script run
  - holds number of inserted and updated players in the last run
  - currently logic located in the script should be implemented inside the database

### database_load.py

Loads the data from a csv file into the database with minor preprocessing of the given data.<br>

### queries.py

Runs several different queries on the database and prints out the result to the standard output<br>

## Instructions
Python 3.11.4<br>
PostgreSQL 16
#### Step 1.
Create virtual environment<br>
#### Step 2.
Activate virtual environment<br>
#### Step 3.
Install dependencies to virtual environment using requirements.txt<br>

```
pip install -r requirements.txt
```
#### Step 4.
Create a .env file with information for connecting to a database<br>
Content of .env file should be formatted in a following way:

```
DB_HOST=xxxxx
DB_USER=xxxxx
DB_PASS=xxxxx
DB_PORT=xxxxx
DB_NAME=xxxxx
```
#### Step 5.
Setup database tables by running:<br>

```
python database_setup.py
```
#### Step 6.
Load existing data(playersData.csv) into database by running database_load.py and passing the filepath as command line argument:<br>

```
python database_load.py <path_to_playersData.csv>
```
#### Step 7.
Run web scraper by passing the filepath to the urls.csv file as command line argument:<br>

```
python player_scrapers.py <path_to_urls>
```
#### Step 8.
Run database_load.py to load the scraped data into the database by passing the filepath to the players_scraped.csv file as command line argument:

```
python database_load.py <path_to_scraped_data>
```

#### Step 9.
Run queries by passing the club name as command line argument:

```
python queries.py <club name>
```
