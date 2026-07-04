import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from models.components import ImageAlternatingModel
from renderers.alternating_renderer import AlternatingRenderer

def test():
    app = QApplication(sys.argv)
    
    # 1. 创建模型
    model = ImageAlternatingModel()
    model.width = 400
    model.height = 300
    
    # 2. 载入测试图片
    test_dir = r"d:\opencode-窗口编辑器迁移尝试\测试图片"
    images = []
    if os.path.exists(test_dir):
        for f in os.listdir(test_dir):
            if f.endswith('.png') or f.endswith('.jpg'):
                images.append(os.path.join(test_dir, f))
    
    model._items = images
    model._item_labels = [os.path.basename(img) for img in images]
    
    # 3. 渲染
    renderer = AlternatingRenderer(model)
    widget = renderer.render()
    
    # 4. 创建窗口显示
    main_win = QMainWindow()
    main_win.setWindowTitle("图片交替变换测试")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.addWidget(widget)
    
    btn_start = QPushButton("开始抽奖 (Start)")
    btn_start.clicked.connect(lambda: model.start_alternating())
    layout.addWidget(btn_start)
    
    btn_stop = QPushButton("停止抽奖 (Stop)")
    btn_stop.clicked.connect(lambda: model.stop_alternating())
    layout.addWidget(btn_stop)
    
    main_win.setCentralWidget(central)
    main_win.resize(450, 400)
    main_win.show()
    
    # 自动测试：开始几秒后停止 (非阻塞)
    from PySide6.QtCore import QTimer
    QTimer.singleShot(1000, lambda: model.start_alternating())
    QTimer.singleShot(3000, lambda: model.stop_alternating())
    QTimer.singleShot(5000, main_win.close) # 自动关闭退出
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test()
