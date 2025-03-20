import maya.mel as mel
import maya.cmds as cmds
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
from maya_reference_manager import MayaReferenceManager
from maya_asset_manager import AssetManager


# 테이블 위젯 내 ui 기능만 배치
class VersionTable:
    def __init__(self):
        # self.setWindowTitle("ASSET & Maya Version Matching Check")
        # self.setGeometry(100, 100, 800, 600)
        # self.setup_ui()
        # self.update_table()
        # self.table.cellClicked.connect(self.onCellClicked)    
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Check Box", "Asset", "Current", "Latest"])
        self.parent = parent
        self.setup_ui()


    def setup_ui(self):
        """UI 요소 초기화 및 설정"""
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Check Box", "Asset", "Current", "Latest"])

        header = self.table.horizontalHeader()
        
        # 체크박스 열만 크기 자동 조정, 나머지는 Stretch
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Check Box 열 크기 조정
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Asset 열
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Current 열
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Latest 열

        header.setMinimumSectionSize(20)  # 최소 크기 제한

        # 버튼 UI
        self.update_button = QPushButton("Update Selected")
        self.update_button.setEnabled(False)  
        self.update_button.clicked.connect(self.apply_selected_versions)

        self.select_all_button = QPushButton("Select All / Deselect All")
        self.select_all_button.clicked.connect(self.toggle_all_checkboxes)

        # 버튼 배치
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.select_all_button)

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)

        self.setCentralWidget(main_widget)

    #정리필요
    def update_table(self):
        self.set_table_items(MayaReferenceManager.get_referenced_assets())


    def set_table_items(self, version_data):
        """테이블 항목 설정"""

        self.table.setRowCount(len(version_data))

        for row, (asset_name, current_version, latest_version) in enumerate(version_data):
            current_version = current_version or "v001"

            try:
                current_version_int = int(re.sub(r"\D", "", current_version))
                latest_version_int = int(re.sub(r"\D", "", latest_version))
            except ValueError:
                current_version_int, latest_version_int = 1, 1

            # Asset 이름 
            asset_item = QTableWidgetItem(asset_name)  
            asset_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, asset_item)

            # Current 버전(콤보박스)
            combo = QComboBox()
            available_versions = AssetManager.get_available_versions(asset_name)
            combo.addItems(available_versions)
            combo.wheelEvent = lambda event: None  # 마우스 휠 비활성화
            combo.setEditable(True)
            combo.lineEdit().setAlignment(Qt.AlignCenter)  # 중앙 정렬 
            for i in range(combo.count()):
                combo.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)


            combo.setCurrentText(f".v{current_version_int:03d}")    # 현재 버전 설정
            combo.currentIndexChanged.connect(lambda _, r=row, c=combo: self.confirm_version_change(r, c))
            self.table.setCellWidget(row, 2, combo)

            # 체크박스 추가
            check_widget = QWidget()
            check_layout = QHBoxLayout()
            check_layout.setAlignment(Qt.AlignCenter)
            check_layout.setContentsMargins(0, 0, 0, 0)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.update_checkbox_state)  # 체크박스 상태 변경 감지
           
            checkbox.setText("✔")
            checkbox.setStyleSheet(
                "QCheckBox {"
                "    color: white;"
                "}"
                "QCheckBox::indicator {"
                "    width: 10px;"
                "    height: 10px;"
                "    border: 1px solid rgb(184, 184, 184);"  # 흰색 테두리
                "    border-radius: 5px;"  # 동그라미 형태로 만들기
                "    background-color: rgb(39, 39, 39);"  # 배경 색상
                "}"
                "QCheckBox::indicator:checked {"
                "    background-color:rgb(184, 184, 184);"  # 체크 시 배경 색상
                "    border: 1px solid rgb(184, 184, 184);"  # 흰색 테두리
                "}"
                "QCheckBox::indicator:checked::after {"
                "    content: '✔';"  # 체크 표시
                "    color: white;"  # 체크 표시 색상 (흰색)
                "    font-size: 2px;"  # 체크 표시 크기
                "    position: absolute;"
              
                "}"
            )

            checkbox.setFixedSize(15, 15)
            check_layout.addWidget(checkbox)
            check_widget.setLayout(check_layout)
            self.table.setCellWidget(row, 0, check_widget)

            # 최신 버전 상태 업데이트 (정수 비교 방식으로 수정)
            latest_status = "🟢" if latest_version_int == current_version_int else "🟡"
            latest_item = QTableWidgetItem(f"{latest_status} {latest_version}")
            latest_item.setTextAlignment(Qt.AlignCenter)
            latest_item.setFlags(Qt.ItemIsEnabled)  # 클릭 비활성화

            # 클릭기능
            self.table.setItem(row, 3, latest_item)
            self.table.cellClicked.connect(self.onCellClicked)