from PyQt6.QtCore import QObject, pyqtSignal

class AnalyticsNotifier(QObject):
    statistics_updated = pyqtSignal(dict)
    plots_updated = pyqtSignal(dict)
    suggestions_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
