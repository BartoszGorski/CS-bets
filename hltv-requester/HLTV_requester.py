import requests
from bs4 import BeautifulSoup
from enum import Enum

import time

HLTV_URL = "http://www.hltv.org/"


class TeamIndex(Enum):
    TEAM_ONE = 0
    TEAM_TWO = 1


class HltvRequester:

    @staticmethod
    def get_parsed_page(url):
        return BeautifulSoup(requests.get(url).text, "lxml")

    def get_matches(self):
        page = self.get_parsed_page("{}matches".format(HLTV_URL))
        matches_dates = page.find("div", {"class": "upcoming-matches"})

        matches = []
        for match_day in matches_dates.find_all("div", {"class": "match-day"}):

            print()
            print('Main loop start')
            start = time.time()

            date = match_day.find('span', {'class': 'standard-headline'}).text
            match_link = match_day.find_all("a", {"class": "a-reset block upcoming-match standard-box"})
            for idx, match in enumerate(match_day.find_all("table", {"class": "table"})):
                new_match = {
                    # 'match_link': match_link[idx]["href"],
                    'date': date,
                    'time': match.find("div", {"class", "time"}).text,
                    'team1': match.find_all("div", {"class": "team"})[TeamIndex.TEAM_ONE.value].text,
                    'team2': match.find_all("div", {"class": "team"})[TeamIndex.TEAM_TWO.value].text,
                    'map': match.find("td", {"class": "star-cell"}).text.strip(),
                    'event': match.find("td", {"class", "event"}).text,
                    'last_matches': self.get_match_details(match_link[idx]["href"]),
                }
                matches.append(new_match)

            end = time.time()
            print('Main loop end = {}'.format(end - start))
        return matches

    @staticmethod
    def check_if_team1_won(match_info):
        if match_info.find('td', {'class', 'won'}):
            return "won"
        else:
            return "lost"

    @staticmethod
    def get_last_matches(table_matches):
        past_matches = []
        for team_table in table_matches:
            team_matches = []
            for match in team_table.find_all('tr', {'class': 'table'}):
                new_match = {
                    'opponent': match.find('td', {'class': 'opponent'}).text.strip(),
                    'score': match.find('td', {'class': 'result'}).text,
                    # 'result': check_if_team1_won(match)
                }
                team_matches.append(new_match)
            past_matches.append(team_matches)
        return past_matches

    @staticmethod
    def get_head_to_head_matches(head_to_head):
        matches = []
        for match in head_to_head.find_all('tr', {'class': 'row'}):
            new_match = {
                'date': match.find('td', {'class': 'date'}).text,
                # 'team1': match.find('td', {'class': 'team1'}).text.strip(),
                # 'team2': match.find('td', {'class': 'team2'}).text.strip(),
                # 'event': match.find('td', {'class': 'event'}).text,
                'result': match.find('td', {'class': 'result'}).text,
            }
            matches.append(new_match)
        return matches

    def get_match_details(self, link):
        page = self.get_parsed_page('{}{}'.format(HLTV_URL, link))

        start = time.time()
        percentage_win_team_1 = page.find('div', {'class': 'pick-a-winner-team team1 canvote'}).find('div', {
            'class': 'percentage'}).text
        percentage_win_team_2 = page.find('div', {'class': 'pick-a-winner-team team2 canvote'}).find('div', {
            'class': 'percentage'}).text
        end = time.time()
        print('percentage = {}'.format(end - start))

        start = time.time()
        last_matches = self.get_last_matches(page.find_all('table', {'class': 'table matches'}))
        end = time.time()
        print('last matches = {}'.format(end - start))

        start = time.time()
        head_to_head = self.get_head_to_head_matches(page.find('div', {'class', 'head-to-head-listing'}))
        end = time.time()
        print('head to head = {}'.format(end - start))

        match_details = {
            'percentage_win_team_1': percentage_win_team_1,
            'percentage_win_team_2': percentage_win_team_2,
            'last_matches': last_matches,
            'head_to_head': head_to_head,
        }
        return match_details

    def get_match_results(self):
        page = self.get_parsed_page("{}results".format(HLTV_URL))
        all_results = page.find_all('div', {'class', 'results-holder'})
        matches_in_dates = all_results[1].find_all('div', {'class': 'results-sublist'})

        matches_list = []
        for matches_one_date in matches_in_dates:
            standard_headline = matches_one_date.find('span', {'class': 'standard-headline'}).text
            for match in matches_one_date.find_all('div', {'class': 'result-con'}):
                new_match = {
                    'head-line': standard_headline,
                    'team1': match.find('div', {'class': 'team1'}).find('div', {'class': 'team'}).text,
                    'team2': match.find('div', {'class': 'team2'}).find('div', {'class': 'team'}).text,
                    'team1-score': match.find('td', {'class': 'result-score'}).find_all('span')[
                        TeamIndex.TEAM_ONE.value].text,
                    'team2-score': match.find('td', {'class': 'result-score'}).find_all('span')[
                        TeamIndex.TEAM_TWO.value].text,
                    'event': match.find('span', {'class': 'event-name'}).text
                }
                matches_list.append(new_match)
        return matches_list
