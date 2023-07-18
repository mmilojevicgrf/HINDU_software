import sys
import time

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen
from hindu_gui import MainWindow


def main():

    window = MainWindow(app)
    window.show()
    splash.finish(window)
    sys.exit(app.exec())


if __name__ == "__main__":

    app = QApplication(sys.argv)
    pixmap = QPixmap("splash.jpg")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("HINDU")
    time.sleep(0.5)
    app.processEvents()

    main()
