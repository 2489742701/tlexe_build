import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Test")
    label = QLabel("Hello from packaged exe!", window)
    window.setCentralWidget(label)
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()