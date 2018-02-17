import requests
from bs4 import BeautifulSoup
from enum import Enum

HLTV_URL = "http://www.hltv.org/"
TEAMS_COUNT = 2
TEAM_PLAYERS_COUNT = 5


class TeamIndex(Enum):
    TEAM_ONE = 0
    TEAM_TWO = 1


class MatchKey(Enum):
    DATE = 'date'
    TIME = 'time'
    TEAM1_NAME = 'team1'
    TEAM2_NAME = 'team2'
    MAP = 'map'
    EVENT = 'event'
    MATCH_LINK = 'match_link'
    MATCH_DETAILS = 'match_details'


class MatchDetailsKey(Enum):
    RESULT = 'result'
    PERCENTAGE_TEAM1 = 'percentage_win_team_1'
    PERCENTAGE_TEAM2 = 'percentage_win_team_2'
    LOGO_TEAM1 = 'team1_logo'
    LOGO_TEAM2 = 'team2_logo'
    LAST_MATCHES = 'last_matches'
    HEAD_2_HEAD = 'head_to_head'
    PLAYERS_TEAMS = 'players_teams'


class PlayerDetails(Enum):
    NICK = 'nick'
    PAGE_LINK = 'page'


class HltvRequester:
    def __init__(self):
        self.page_matches = None
        self.match_days = None

        self.prepare_matches_data()

    def prepare_matches_data(self):
        self.page_matches = self.get_parsed_page("{}matches".format(HLTV_URL))
        self.match_days = self.page_matches.find_all("div", {"class": "match-day"})

    @staticmethod
    def get_parsed_page(url):
        return BeautifulSoup(requests.get(url).text, "lxml")

    def get_matches_count(self, days=3):
        length_match_days = len(self.match_days)
        if days > length_match_days:
            days = length_match_days
        matches_count_in_day = []
        for day_idx in range(days):
            matches_count_in_day.append(len(self.match_days[day_idx].find_all("td", {"class": "vs"})))
        return matches_count_in_day

    def get_matches_of_day(self, match_day_idx):
        matches = []
        date = self.match_days[match_day_idx].find('span', {'class': 'standard-headline'}).text
        match_link = self.match_days[match_day_idx].find_all("a", {"class": "a-reset block upcoming-match standard-box"})

        for idx, match in enumerate(self.match_days[match_day_idx].find_all("table", {"class": "table"})):
            teams = match.find_all("div", {"class": "team"})
            if not teams:
                continue
            new_match = {
                MatchKey.DATE.value: date,
                MatchKey.TIME.value: match.find("div", {"class", "time"}).text,
                MatchKey.TEAM1_NAME.value: teams[TeamIndex.TEAM_ONE.value].text,
                MatchKey.TEAM2_NAME.value: teams[TeamIndex.TEAM_TWO.value].text,
                MatchKey.MAP.value: match.find("td", {"class": "star-cell"}).text.strip(),
                MatchKey.EVENT.value: match.find("td", {"class", "event"}).text,
                MatchKey.MATCH_LINK.value: match_link[idx]["href"],
                #TODO check if it is better way to get match link
                # 'last_matches': self.get_match_details(match_link[match_idx]["href"]),
            }
            matches.append(new_match)
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
                # 'date': match.find('td', {'class': 'date'}).text,
                # 'team1': match.find('td', {'class': 'team1'}).text.strip(),
                # 'team2': match.find('td', {'class': 'team2'}).text.strip(),
                # 'event': match.find('td', {'class': 'event'}).text,
                MatchDetailsKey.RESULT.value: match.find('td', {'class': 'result'}).text,
            }
            matches.append(new_match)
        return matches

    def get_players(self, lineups):
        players_nicks_count_on_page = 10
        team_players = []
        for team in range(TEAMS_COUNT):
            players = []
            players_td = lineups[team].find_all('td', {'class': 'player'})
            for player_index in range(TEAM_PLAYERS_COUNT, players_nicks_count_on_page):
                player_link = players_td[player_index].find('a')
                new_player = {
                    PlayerDetails.PAGE_LINK.value: player_link['href'] if player_link else "Player does not have page",
                    PlayerDetails.NICK.value: players_td[player_index].find('div', {'class': 'text-ellipsis'}).text,
                }
                players.append(new_player)
            team_players.append(players)
        return team_players

    def get_match_details(self, link):
        page = self.get_parsed_page('{}{}'.format(HLTV_URL, link))

        teams_logo = page.find_all('img', {'class': 'logo'})
        team1_logo = teams_logo[TeamIndex.TEAM_ONE.value]['src']
        team2_logo = teams_logo[TeamIndex.TEAM_TWO.value]['src']
        lineups = page.find_all('div', {'class': 'lineup standard-box'})
        team_players = self.get_players(lineups)

        percentage_win_team_1 = page\
            .find('div', {'class': 'pick-a-winner-team team1 canvote'})\
            .find('div', {'class': 'percentage'}).text
        percentage_win_team_2 = page\
            .find('div', {'class': 'pick-a-winner-team team2 canvote'})\
            .find('div', {'class': 'percentage'}).text

        last_matches = self.get_last_matches(page.find_all('table', {'class': 'table matches'}))
        head_to_head = self.get_head_to_head_matches(page.find('div', {'class', 'head-to-head-listing'}))

        match_details = {
            MatchDetailsKey.LOGO_TEAM1.value: team1_logo,
            MatchDetailsKey.LOGO_TEAM2.value: team2_logo,
            MatchDetailsKey.PERCENTAGE_TEAM1.value: percentage_win_team_1,
            MatchDetailsKey.PERCENTAGE_TEAM2.value: percentage_win_team_2,
            MatchDetailsKey.LAST_MATCHES.value: last_matches,
            MatchDetailsKey.HEAD_2_HEAD.value: head_to_head,
            MatchDetailsKey.PLAYERS_TEAMS.value: team_players,
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
