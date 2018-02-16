# !/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from WindowManager import WindowManager


def setup_signals(window_manager):
    window_manager.matches_list.itemClicked.connect(window_manager.show_match_details)


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window_manager = WindowManager(window)
    setup_signals(window_manager)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
        main()
