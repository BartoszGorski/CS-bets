import threading

from GUI.MainWindow import Ui_MainWindow
from hltvRequester.HLTV_requester import HltvRequester


class WindowManager(Ui_MainWindow):
    def __init__(self, main_window):
        self.setupUi(main_window)
        main_window.show()
        self.hltv = HltvRequester()

        t = threading.Thread(target=self.show_matches)
        t.start()

    def show_matches(self):
        matches_count_in_day = self.hltv.get_matches_count(days=3)
        for match_day_idx in range(len(matches_count_in_day)):
            for match_idx in range(matches_count_in_day[match_day_idx]):
                self.matches_list.addItem(self.parse_match_dict_to_string(
                        self.hltv.get_individual_match(match_day_idx, match_idx)
                ))

    def parse_match_dict_to_string(self, match_dictionary):
        return "{} - {}\t{} vs {}\t{}\t{}".format(
            match_dictionary.get("date"), match_dictionary.get("time"),
            match_dictionary.get("team1"), match_dictionary.get("team2"),
            match_dictionary.get("map"), match_dictionary.get("event")
        )
