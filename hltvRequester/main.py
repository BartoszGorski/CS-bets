import requests
from bs4 import BeautifulSoup
from python_utils import converters
import pprint
from enum import Enum

###

import os, sys

if sys.version_info.major < 3:
    from urllib import url2pathname
else:
    from urllib.request import url2pathname

class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):  # pylint: disable=unused-argument
        """Return the file specified by the given request

        @type req: C{PreparedRequest}
        @todo: Should I bother filling `response.headers` and processing
               If-Modified-Since and friends using `os.stat`?
        """
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass

###


import time


HLTV_URL = "http://www.hltv.org/"


class TeamIndex(Enum):
    TEAM_ONE = 0
    TEAM_TWO = 1


def get_parsed_page(url):
    # requests_session = requests.session()
    # requests_session.mount('file://', LocalFileAdapter())
    # r = requests_session.get(url)

    return BeautifulSoup(requests.get(url).text, "lxml")
    # return BeautifulSoup(r.text, "lxml")


def top30teams():
    page = get_parsed_page("{}ranking/teams/".format(HLTV_URL))
    teams = page.find("div", {"class": "ranking"})
    teamlist = []
    for team in teams.find_all("div", {"class": "ranked-team standard-box"}):
        team.find('div', {"class": "header"})
        newteam = {'name': team.select('.name')[0].text.strip(),
                   'rank': converters.to_int(team.select('.position')[0].text.strip(), regexp=True),
                   'rank-points': converters.to_int(team.find('span', {'class': 'points'}).text, regexp=True),
                   'team-id': converters.to_int(team.select('.name')[0]["data-url"].split("/")[2], regexp=True),
                   'team-players': []}
        for player_div in team.find_all("td", {"class": "player-holder"}):
            player = {}
            player['name'] = player_div.find('img', {'class': 'playerPicture'})['title']
            player['player-id'] = converters.to_int(player_div.find('span', {"class": "js-link"})['data-url'].split("/")[2])
            newteam['team-players'].append(player)
        teamlist.append(newteam)
    return teamlist


def get_matches():
    page = get_parsed_page("{}matches".format(HLTV_URL))
    # page = get_parsed_page("file:///home/baal/workspace/hltv-webpage/CS_GO%20Matches%20&%20livescore%20_%20HLTV.org.html")
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
                'last_matches': get_match_details(match_link[idx]["href"]),
            }
            matches.append(new_match)

        end = time.time()
        print('Main loop end = {}'.format(end - start))

    return matches


def check_if_team1_won(match_info):
    if match_info.find('td', {'class', 'won'}):
        return "won"
    else:
        return "lost"


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


def get_match_details(link):
    # page = get_parsed_page(
    #     "file:///home/baal/workspace/hltv-webpage/AGO%20vs.%20AVANGAR%20at%20Farmskins%20Championship%20%232%20-%20IEM%20Katowice%202018%20Qualifier%20_%20HLTV.org.html")

    page = get_parsed_page('{}{}'.format(HLTV_URL, link))

    start = time.time()
    percentage_win_team_1 = page.find('div', {'class': 'pick-a-winner-team team1 canvote'}).find('div', {'class': 'percentage'}).text
    percentage_win_team_2 = page.find('div', {'class': 'pick-a-winner-team team2 canvote'}).find('div', {'class': 'percentage'}).text
    end = time.time()
    print('percentage = {}'.format(end - start))

    start = time.time()
    last_matches = get_last_matches(page.find_all('table', {'class': 'table matches'}))
    end = time.time()
    print('last matches = {}'.format(end - start))

    start = time.time()
    head_to_head = get_head_to_head_matches(page.find('div', {'class', 'head-to-head-listing'}))
    end = time.time()
    print('head to head = {}'.format(end - start))

    match_details = {
        'percentage_win_team_1': percentage_win_team_1,
        'percentage_win_team_2': percentage_win_team_2,
        'last_matches': last_matches,
        'head_to_head': head_to_head,
    }
    return match_details


def get_match_results():
    # page = get_parsed_page("file:///home/baal/workspace/hltv-webpage/CS_GO%20Results%20_%20HLTV.org.html")
    page = get_parsed_page("{}results".format(HLTV_URL))
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
                'team1-score': match.find('td', {'class': 'result-score'}).find_all('span')[TeamIndex.TEAM_ONE.value].text,
                'team2-score': match.find('td', {'class': 'result-score'}).find_all('span')[TeamIndex.TEAM_TWO.value].text,
                'event': match.find('span', {'class': 'event-name'}).text
            }
            matches_list.append(new_match)
    return matches_list


def main():
    pp = pprint.PrettyPrinter()
    pp.pprint(get_matches())


if __name__ == "__main__":
    main()
