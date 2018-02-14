# !/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from WindowManager import WindowManager


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    WindowManager(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
        main()
