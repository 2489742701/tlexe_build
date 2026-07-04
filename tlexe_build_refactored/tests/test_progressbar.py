"""进度条测试文件。"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QWidget, QPushButton

class TestProgressBar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("进度条测试")
        self.resize(400, 200)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.btn = QPushButton("开始")
        self.btn.clicked.connect(self._on_click)
        layout.addWidget(self.btn)
        
        self._value = 0
    
    def _on_click(self):
        self._value += 10
        if self._value > 100:
            self._value = 0
        self.progress.setValue(self._value)

def main():
    app = QApplication(sys.argv)
    window = TestProgressBar()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
