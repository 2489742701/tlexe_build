"""导航管理器模块。

本模块负责管理欢迎页和编辑器窗口之间的导航切换，
将 AppManager 中的窗口管理职责分离出来。

"""

from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import QObject, Signal

from utils.session_logger import SessionLogger

class NavigationManager(QObject):
    """导航管理器 - 处理欢迎页/编辑器之间的导航。

    Signals:
        navigation_changed: 导航页面切换时发射 (page_name)
    """

    navigation_changed = Signal(str)

    PAGE_WELCOME = "welcome"
    PAGE_EDITOR = "editor"

    def __init__(self, session_logger: SessionLogger = None):
        super().__init__()
        self._session_logger = session_logger
        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setWindowTitle("UI快速开发工具")
        self._stacked_widget.resize(1200, 800)
        self._welcome_page = None
        self._main_window = None
        self._current_page = None

    @property
    def stacked_widget(self) -> QStackedWidget:
        return self._stacked_widget

    @property
    def welcome_page(self):
        return self._welcome_page

    @welcome_page.setter
    def welcome_page(self, page):
        if self._welcome_page is not None and self._stacked_widget.indexOf(self._welcome_page) == -1:
            pass
        self._welcome_page = page
        if page is not None:
            self._stacked_widget.addWidget(page)

    @property
    def main_window(self):
        return self._main_window

    @main_window.setter
    def main_window(self, window):
        self._main_window = window
        if window is not None and self._stacked_widget.indexOf(window) == -1:
            self._stacked_widget.addWidget(window)

    def show_welcome(self):
        if self._welcome_page is None:
            if self._session_logger:
                self._session_logger.log("ERROR", "欢迎页实例为 None，无法切换")
            return

        self._stacked_widget.setCurrentWidget(self._welcome_page)
        self._stacked_widget.setWindowTitle("UI快速开发工具")
        self._current_page = self.PAGE_WELCOME
        self.navigation_changed.emit(self.PAGE_WELCOME)

        try:
            self._welcome_page.refresh_data()
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("WARNING", f"欢迎页刷新异常: {e}")

    def show_editor(self, project_name: str = ""):
        if self._main_window is None:
            if self._session_logger:
                self._session_logger.log("ERROR", "编辑器窗口实例为 None，无法切换")
            return

        self._stacked_widget.setCurrentWidget(self._main_window)
        title = f"{project_name} - UI快速开发工具" if project_name else "UI快速开发工具"
        self._stacked_widget.setWindowTitle(title)
        self._current_page = self.PAGE_EDITOR
        self.navigation_changed.emit(self.PAGE_EDITOR)

    @property
    def current_page(self) -> str:
        return self._current_page

    def show(self):
        self._stacked_widget.show()