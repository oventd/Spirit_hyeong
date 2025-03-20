try:
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile
    from PySide6.QtWidgets import QWidget, QApplication

except:
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile
    from PySide2.QtWidgets import QWidget, QApplication



class UILoader:
    _instance = None

    def __new__(cls, ui_file_path):
        if not cls._instance:
            cls._instance = super(UILoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, ui_file_path):
        if hasattr(self, "_initialized"):  # 중복 초기화 방지
            return
        self._initialized = True  # 초기화 완료 여부 체크

        self.ui_file_path = ui_file_path
        self.ui = None

    def load_ui(self) -> QWidget:
        """ UI 파일을 로드하고 QWidget 객체를 반환 """
        if self.ui is None:
            ui_file = QFile(self.ui_file_path)
            loader = QUiLoader()
            self.ui = loader.load(ui_file)
            ui_file.close()
            self.ui.setStatusBar(None)
            self.ui.setFixedSize(1240, 799)
            self.center()
        return self.ui

    def center(self):
        screen = QApplication.primaryScreen()  #  QApplication을 사용하여 기본 화면 가져오기
        screen_geometry = screen.availableGeometry()  #  사용 가능한 화면 크기 가져오기
        x = (screen_geometry.width() - self.ui.width()) // 2
        y = (screen_geometry.height() - self.ui.height()) // 2
        self.ui.move(x, y)  #  화면 중앙으로 이동

