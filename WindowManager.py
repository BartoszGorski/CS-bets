import threading
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets

from GUI.MainWindow import Ui_MainWindow
from hltvRequester.HLTV_requester import HltvRequester, TeamIndex
from hltvRequester.HLTV_requester import MatchKey, MatchDetailsKey, PlayerDetails
from hltvRequester.HLTV_requester import TEAMS_COUNT, TEAM_PLAYERS_COUNT

from urllib.request import Request, urlopen


class WindowManager(Ui_MainWindow):
    def __init__(self, main_window):
        self.setupUi(main_window)
        self.center_window(main_window)
        self.setup_components()
        self.hltv = HltvRequester()
        self.matches = []
        self.download_matches()

    def center_window(self, window):
        frame_geometry = window.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        window.move(frame_geometry.topLeft())

    def download_matches(self):
        t = threading.Thread(target=self.show_matches)
        t.start()

    def setup_components(self):
        self.t1_image_label.setScaledContents(True)
        self.t2_image_label.setScaledContents(True)

    def show_matches(self, match_days=3):
        for match_day_idx in range(match_days):
            matches = self.hltv.get_matches_of_day(match_day_idx)
            self.matches.extend(matches)

        for match in self.matches:
            self.matches_list.addItem(self.parse_match_dict_to_string(match))

    def parse_match_dict_to_string(self, match_dictionary):
        return "{} - {}\t{} vs {}\t{}\t{}".format(
            match_dictionary.get(MatchKey.DATE.value), match_dictionary.get(MatchKey.TIME.value),
            match_dictionary.get(MatchKey.TEAM1_NAME.value), match_dictionary.get(MatchKey.TEAM2_NAME.value),
            match_dictionary.get(MatchKey.MAP.value), match_dictionary.get(MatchKey.EVENT.value)
        )

    def show_match_details(self):
        self.statusbar.showMessage("loading data...", msecs=2000)
        list_row_index = self.matches_list.currentRow()
        match_details = {}
        try:
            match_details = self.get_match_details(list_row_index)
        except Exception:
            error_msg = "Can not find all details about {} vs. {} match".format(
                self.matches[list_row_index][MatchKey.TEAM1_NAME.value],
                self.matches[list_row_index][MatchKey.TEAM2_NAME.value]
            )
            self.statusbar.showMessage(error_msg, msecs=2000)

        self.date_label.setText(self.matches[list_row_index][MatchKey.DATE.value])
        self.time_label.setText(self.matches[list_row_index][MatchKey.TIME.value])
        self.t1_name_label.setText(self.matches[list_row_index][MatchKey.TEAM1_NAME.value])
        self.t2_name_label.setText(self.matches[list_row_index][MatchKey.TEAM2_NAME.value])

        if match_details:
            self.t1_percentage.setText(self.matches[list_row_index][MatchKey.MATCH_DETAILS.value][
                                           MatchDetailsKey.PERCENTAGE_TEAM1.value])
            self.t2_percentage.setText(self.matches[list_row_index][MatchKey.MATCH_DETAILS.value][
                                           MatchDetailsKey.PERCENTAGE_TEAM2.value])
            url = self.matches[list_row_index][MatchKey.MATCH_DETAILS.value][
                MatchDetailsKey.LOGO_TEAM1.value]
            self.set_team_logo(TeamIndex.TEAM_ONE, url)
            url = self.matches[list_row_index][MatchKey.MATCH_DETAILS.value][
                MatchDetailsKey.LOGO_TEAM2.value]
            self.set_team_logo(TeamIndex.TEAM_TWO, url)

            for team_index in range(TEAMS_COUNT):
                for player_index in range(TEAM_PLAYERS_COUNT):
                    self.get_player_label(team_index+1, player_index+1).setText(
                        self.matches[list_row_index]
                        [MatchKey.MATCH_DETAILS.value]
                        [MatchDetailsKey.PLAYERS_TEAMS.value]
                        [team_index]
                        [player_index]
                        [PlayerDetails.NICK.value])

    def get_player_label(self, team, player):
        labels = {
            "t1_p1": self.t1_p1,
            "t1_p2": self.t1_p2,
            "t1_p3": self.t1_p3,
            "t1_p4": self.t1_p4,
            "t1_p5": self.t1_p5,
            "t2_p1": self.t2_p1,
            "t2_p2": self.t2_p2,
            "t2_p3": self.t2_p3,
            "t2_p4": self.t2_p4,
            "t2_p5": self.t2_p5,
        }
        return labels["t{}_p{}".format(team, player)]

    def set_team_logo(self, team, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if team == TeamIndex.TEAM_ONE:
            self.t1_image_label.setPixmap(pixmap)
            self.t1_image_label.show()
        elif team == TeamIndex.TEAM_TWO:
            self.t2_image_label.setPixmap(pixmap)
            self.t2_image_label.show()

    def get_match_details(self, list_row_index):
        match_link = self.matches[list_row_index][MatchKey.MATCH_LINK.value]
        match_details = self.hltv.get_match_details(match_link)
        self.matches[list_row_index][MatchKey.MATCH_DETAILS.value] = match_details
        return match_details
