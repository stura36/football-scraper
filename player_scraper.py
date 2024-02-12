import pandas as pd
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import re


class Extractor:
    """
    Class for extracting player data from a wikipedia page
    For each information, a method is defined to extract the data
    For data to be extracted, the infobox with data must exist
    """

    def __init__(self, soup):
        self.soup = soup
        self.infobox = self.extract_info_box()

    def extract_player_name(self):
        player_name = self.soup.find("span", class_="mw-page-title-main").text
        player_name = self.extract_text_outside_brackets(player_name)
        return player_name

    def extract_info_box(self):
        infobox = self.soup.find(class_="infobox vcard")
        return infobox

    def extract_player_full_name(self, player_name):
        player_full_name = self.infobox.find("td", class_="infobox-data nickname")
        if player_full_name:
            player_full_name = player_full_name.text
        else:
            player_full_name = player_name

        player_full_name = self.extract_text_outside_brackets(player_full_name)
        return player_full_name

    def extract_dob(self):
        dob = self.infobox.find("span", class_="bday")
        if dob is None:
            return None
        dob = dob.text
        dob = self.extract_text_outside_brackets(dob)
        return dob

    def extract_age(self):
        age = self.infobox.find("span", class_="noprint ForceAgeToShow")
        if age is None:
            return None

        age = age.text
        age = age.split("\xa0")[1][:-1]
        age = int(age)

        return age

    def extract_place_of_birth(self):
        place_of_birth = self.infobox.find("td", class_="infobox-data birthplace")
        if place_of_birth is None:
            return None
        place_of_birth = place_of_birth.text
        place_of_birth = self.extract_text_outside_brackets(place_of_birth)
        list_places = place_of_birth.split(",")
        if len(list_places) > 1:
            place_of_birth = list_places[:-1]
            place_of_birth = ",".join(place_of_birth)

        return place_of_birth

    def extract_country_of_birth(self):
        place_of_birth = self.infobox.find("td", class_="infobox-data birthplace")
        if place_of_birth is None:
            return None
        place_of_birth = place_of_birth.text
        list_places = place_of_birth.split(",")
        country_of_birth = list_places[-1]
        country_of_birth = self.extract_text_outside_brackets(country_of_birth)
        return country_of_birth

    def extract_position(self):
        position = self.infobox.find("td", class_="infobox-data role")
        if position:
            position = position.text
            position = position.split(",")
            position = position[-1]
            position = self.extract_text_outside_brackets(position)

        return position

    def extract_current_club(self):
        current_club = self.infobox.find("td", class_="infobox-data org")
        if current_club:
            current_club = current_club.text
            current_club = self.extract_text_outside_brackets(current_club)
        return current_club

    def extract_text_outside_brackets(self, text):

        match = re.sub(r"[\(\[\{].*?[\)\]\}]", "", text)
        match = match.strip()
        return match

    def extract_apps_goals_national_team(self, club_name):

        teams = self.infobox.find_all(class_="infobox-data infobox-data-a")
        apps = self.infobox.find_all(class_="infobox-data infobox-data-b")
        goals = self.infobox.find_all(class_="infobox-data infobox-data-c")
        infobox_headers = self.infobox.find_all(class_="infobox-header")
        has_nat_team = False

        for i, header in enumerate(infobox_headers):
            if "international career" in header.text.lower().strip():
                has_nat_team = True
                break

        app_sum = 0
        goal_sum = 0

        for i, team in enumerate(teams):
            team_text = self.extract_text_outside_brackets(team.text)
            if club_name == team_text:
                app_text = apps[i].text.strip()
                goal_text = goals[i].text.strip()

                if app_text.isspace() or app_text == "?" or app_text == "":
                    app_text = "0"
                if goal_text.isspace() or goal_text == "?" or goal_text == "":
                    goal_text = "(0)"

                apps_i = int(app_text)
                app_sum += apps_i
                goals_i = int(goal_text[1:-1])
                goal_sum += goals_i

        if len(teams) == 0:
            return None, None, None
        if has_nat_team:
            nat_team = self.extract_text_outside_brackets(teams[-1].text)
        else:
            nat_team = None

        return app_sum, goal_sum, nat_team

    def get_info_box(self):
        return self.infobox


class PlayerScraper:
    """Main class used for webscraping list of football player urls from
    wikipedia page"""

    def __init__(self):
        self.dict_entries = {
            "URL": [],
            "Name": [],
            "Full name": [],
            "Date of birth": [],
            "Age": [],
            "Place of birth": [],
            "Country of birth": [],
            "Position": [],
            "Current club": [],
            "National team": [],
            "Appearance count": [],
            "Goal count": [],
            "Scrap timestamp": [],
        }

    def load_urls(self, filename):
        "Load urls from .csv file"
        urls = pd.read_csv(filename)
        urls = urls.values.tolist()
        return urls

    def scrape_page(self, response):
        """
        Perform extraction for each feature and store it into dictionary
        """
        soup = BeautifulSoup(response.text, "html.parser")

        ex = Extractor(soup)

        if not ex.get_info_box():
            return False

        player_name = ex.extract_player_name()
        player_full_name = ex.extract_player_full_name(player_name)
        dob = ex.extract_dob()
        age = ex.extract_age()
        place_of_birth = ex.extract_place_of_birth()
        country_of_birth = ex.extract_country_of_birth()
        position = ex.extract_position()
        current_club = ex.extract_current_club()
        apps, goals, country = ex.extract_apps_goals_national_team(current_club)

        self.dict_entries["Scrap timestamp"].append(datetime.now())
        self.dict_entries["Name"].append(player_name)
        self.dict_entries["Full name"].append(player_full_name)
        self.dict_entries["Date of birth"].append(dob)
        self.dict_entries["Age"].append(age)
        self.dict_entries["Place of birth"].append(place_of_birth)
        self.dict_entries["Country of birth"].append(country_of_birth)
        self.dict_entries["Position"].append(position)
        self.dict_entries["Current club"].append(current_club)
        self.dict_entries["National team"].append(country)
        self.dict_entries["Appearance count"].append(apps)
        self.dict_entries["Goal count"].append(goals)

        return True

    def iterate_urls(self, urls):
        """Pass through list urls and web scrap each page connected to the url"""
        for url in tqdm(urls):
            response = requests.get(url[0])
            player_entry_flag = self.scrape_page(response)
            if player_entry_flag:
                self.dict_entries["URL"].append(url[0])

        self.store_data("players_scraped.csv")
        return

    def store_data(self, filepath):
        """Store data into .csv file"""
        df = pd.DataFrame(
            self.dict_entries,
        )

        df["Appearance count"] = df["Appearance count"].astype("Int32")
        df["Goal count"] = df["Goal count"].astype("Int32")
        df["Age"] = df["Age"].astype("Int32")

        df.to_csv(filepath, index=False, sep=";")
        return


if __name__ == "__main__":
    urls_path = sys.argv[1]
    scraper = PlayerScraper()
    urls = scraper.load_urls(urls_path)
    scraper.iterate_urls(urls)
