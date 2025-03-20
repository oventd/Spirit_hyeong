# import maya.mel as mel
# import maya.cmds as cmds
import sys
import os
import re
try:
    from PySide6.QtWidgets import (
        QMainWindow, QApplication, QWidget, QTableWidget, QTableWidgetItem,
        QPushButton, QHeaderView, QCheckBox, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
    )
    from PySide6.QtCore import QFile, Qt
    from PySide6.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import (
        QMainWindow, QApplication, QWidget, QTableWidget, QTableWidgetItem,
        QPushButton, QHeaderView, QCheckBox, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
    )
    from PySide2.QtCore import QFile, Qt
    from PySide2.QtGui import QColor

sys.path.append('/home/rapa/NA_Spirit/maya')

from maya_ui_manager import MainUiManager
from maya_asset_manager import AssetManager
from maya_reference_manager import MayaReferenceManager

class MainUi(QMainWindow):
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MainUi, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # 중복 초기화를 방지
            self._initialized = True
            super().__init__()

  
            self.main_ui_manager = MainUiManager()
            self.setCentralWidget(self.main_ui_manager)
            self.asset_manager = AssetManager()
            self.reference_manager = MayaReferenceManager()

            
if __name__ == "__main__":
    window = MainUi()
    window.show()

