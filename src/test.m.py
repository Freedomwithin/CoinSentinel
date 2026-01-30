from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from api_handler import EnhancedCryptoAPIHandler
from improved_market_tab import ImprovedMarketTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Tracker")
        self.setGeometry(100, 100, 800, 600)

        api = EnhancedCryptoAPIHandler()
        self.tabs = QTabWidget()
        self.tabs.addTab(ImprovedMarketTab(api), "Market Overview")

        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
