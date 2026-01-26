# test_minimal.py - Minimal test without ML
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - CoinSentinel")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        label = QLabel("CoinSentinel Loading...\\nIf this appears, GUI works!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; padding: 50px;")
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
