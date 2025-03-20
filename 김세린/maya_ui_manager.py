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

import maya.cmds as cmds

from maya_reference_manager import MayaReferenceManager
from maya_asset_manager import AssetManager

ASSET_DIRECTORY = "/nas/spirit/spirit/assets/Prop"

# 테이블의 기능 구현 

class MainUiManager(QMainWindow):
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # 인스턴스가 없다면 생성
            cls._instance = super(MainUiManager, cls).__new__(cls)
        return cls._instance  # 이미 존재하는 인스턴스를 반환

    def __init__(self):
        if not hasattr(self, "_initialized"):  # 초기화 여부 체크
            self._initialized = True
            super().__init__()

            self.setWindowTitle("ASSET & Maya Version Matching Check")
            self.setGeometry(100, 100, 900, 600)
            self.setup_ui()
            self.update_table()

            self.table.cellClicked.connect(self.onCellClicked)


            
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

        self.refresh_maya_reference_button = QPushButton("Refresh Maya Reference")
        self.refresh_maya_reference_button.clicked.connect(self.refresh_maya_reference)

        self.select_all_button = QPushButton("Select All / Deselect All")
        self.select_all_button.clicked.connect(self.toggle_all_checkboxes)

        # 버튼 배치
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.refresh_maya_reference_button)
        button_layout.addWidget(self.select_all_button)
        

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)

        self.setCentralWidget(main_widget)
    
    #정리필요
    def update_table(self):
        try:
            referenced_assets = MayaReferenceManager.get_referenced_assets()
            if not referenced_assets:
                print("⚠️ 참조된 에셋이 없습니다.")
                return

            # 기존 테이블 항목 초기화 (행 삭제)
            self.table.setRowCount(0)

            # 에셋 정보를 테이블에 추가
            self.set_table_items(referenced_assets)
        except Exception as e:
            print(f"⚠️ 에셋 정보를 불러오는 중 오류 발생: {e}")
    def set_table_items(self, version_data):
        """테이블 항목 설정"""

        self.table.setRowCount(len(version_data))

        for row, (asset_name, current_version, latest_version) in enumerate(version_data):
            current_version = current_version or "v001"
            latest_version = AssetManager.get_latest_version(asset_name)

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


    def update_checkbox_state(self):
        """체크박스 상태 변경 시 Update Selected 버튼 활성화"""
        checked = False
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if widget and widget.layout():  # 🔹 체크박스가 존재하는지 확인
                checkbox = widget.layout().itemAt(0).widget()
                if checkbox and checkbox.isChecked():
                    checked = True
                    break
        self.update_button.setEnabled(checked)

        # 추가만 해주면됨

    def apply_selected_versions(self):
        """선택된 항목을 최신 버전으로 업데이트"""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0).layout().itemAt(0).widget()
            if checkbox.isChecked():
                combo = self.table.cellWidget(row, 2)
                latest_item = self.table.item(row, 3)
                selected_version = combo.currentText()  # 콤보박스에서 선택된 버전

                # Maya에서 참조를 실제로 갱신
                self.update_maya_reference(row, selected_version)  # 선택된 버전의 텍스트를 전달

                # UI 갱신 (최신 버전 확인 후 상태 갱신)
                latest_version = AssetManager.get_latest_version(self.table.item(row, 1).text())
                self.update_version_status(row, combo, latest_item)  # UI 갱신
                self.table.setItem(row, 3, latest_item)  # 'Latest' 열을 갱신


    def refresh_maya_reference(self):
        references = cmds.file(q=True, reference=True) or []
        for ref in references:
            try:
                # 참조 노드를 찾기 전에 참조를 언로드
                ref_node = cmds.referenceQuery(ref, referenceNode=True)
                cmds.file(unloadReference=ref_node)  # 참조 파일 언로드

                # 참조 파일의 최신 버전 경로 얻기
                latest_ref_path = cmds.referenceQuery(ref, filename=True)  # 레퍼런스 조회
                cmds.file(latest_ref_path, loadReference=ref_node, force=True)  # 최신 버전으로 참조 파일 로드

                print(f"참조 업데이트 완료: {ref}")

                # 테이블에서 참조 파일의 최신 버전으로 업데이트
                row = self.find_reference_row(ref)  # 테이블에서 참조 파일이 있는 행을 찾음
                if row is not None:
                    # 최신 버전 가져오기 (예: AssetManager에서 최신 버전 조회)
                    latest_version = AssetManager.get_latest_version(ref)  # 최신 버전 정보 얻기
                    
                    # 디버깅: 최신 버전이 잘 반환되는지 확인
                    print(f"최신 버전: {latest_version}")

                    # 테이블에서 해당 행의 'Latest' 열 업데이트
                    latest_item = self.table.item(row, 3)
                    if latest_item is not None:
                        latest_item.setText(latest_version)  # 'Latest' 열 업데이트
                    else:
                        print("Error: 'Latest' 열이 비어있습니다.")

                    # 'Current' 열도 최신 버전으로 업데이트
                    current_item = self.table.item(row, 2)
                    if current_item is not None:
                        current_item.setText(latest_version)  # 'Current' 열 업데이트
                    else:
                        print("Error: 'Current' 열이 비어있습니다.")

                # UI 테이블 갱신
                self.update_table()

            except Exception as e:
                print(f"⚠️ 참조 업데이트 실패: {e}")


    def find_reference_row(self, ref):
        """
        테이블에서 참조 파일에 해당하는 행을 찾아 반환합니다.
        참조 파일의 이름 또는 경로를 기준으로 테이블에서 해당 행을 찾는 로직입니다.
        """
        for row in range(self.table.rowCount()):
            # 테이블의 'Asset' 열에서 참조 파일을 찾기
            asset_name = self.table.item(row, 0).text()  # 'Asset' 열 (예: 첫 번째 열)
            if asset_name == ref:  # 참조 파일 이름과 일치하는지 비교
                return row
        return None


    def toggle_all_checkboxes(self):
        """모든 체크박스를 선택/해제하는 기능"""
        checkboxes = [
            self.table.cellWidget(row, 0).layout().itemAt(0).widget()
            for row in range(self.table.rowCount())
        ]
        new_state = Qt.Unchecked if all(cb.isChecked() for cb in checkboxes) else Qt.Checked

        for cb in checkboxes:
            cb.setChecked(new_state)

    def update_version_status(self, row, combo, latest_item):
        """최신 버전 상태 UI 업데이트"""
        asset_name = self.table.item(row, 1).text()
        latest_version = AssetManager.get_latest_version(asset_name)  #  최신 버전 다시 가져오기

        # 버전 비교 전에 .v를 제거하고 숫자만 남기기
        current_version_str = combo.currentText().replace("v", "").replace(".", "")  # .v와 .을 모두 제거
        latest_version_str = latest_version.replace("v", "").replace(".", "")  # 최신 버전에서 .v와 .을 제거

        try:
            # 현재 버전과 최신 버전을 숫자 비교 가능하도록 정수로 변환
            current_version = int(current_version_str)  # 현재 버전 (숫자)
            latest_version_int = int(latest_version_str)  # 최신 버전 (숫자)
            print ( current_version)
        except ValueError as e:
            print(f"버전 값 변환 오류: {e}")
            return

        # 최신 상태 반영 (🟢 최신 / 🟡 구버전)
        latest_status = "🟢" if current_version == latest_version_int else "🟡"
        latest_item.setText(f"{latest_status} v{latest_version_int:03d}")

        # UI 갱신 적용
        self.table.setItem(row, 3, latest_item)

        print(f"최신 버전 갱신됨: {asset_name} | 현재: v{current_version} | 최신: v{latest_version_int}")


    def confirm_version_change(self, row, combo):
        """버전 변경 시 메시지 박스를 UI 클래스에서 처리"""
        new_version = combo.currentText().replace(".", "").strip()  # 선택된 버전 텍스트 가져오기

        # 사용자에게 확인 메시지 표시
        msg = QMessageBox.warning(
            self, "Confirm Change",
            f"Do you really want to change the version to .v{new_version:03d}?",  # 버전 형식 맞춰서 표시
            QMessageBox.Yes | QMessageBox.No
        )
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirm Version Change")
        msg.setText(f"Change version to .v{new_version:03d}?")  # .v{new_version:03d} 형태로 정확한 버전 표시

        reply = msg.exec()  # exec()로 대기하여 메시지 박스가 닫히기를 기다림

        if reply == QMessageBox.Yes:
            # 버전 업데이트 진행
            version = f".v{new_version:03d}"
            self.update_maya_reference(row, version)  # 선택된 버전으로 참조 업데이트

            # 콤보박스와 최신 버전 상태 업데이트
            combo.setCurrentText(f".v{new_version:03d}")  # 콤보박스를 .v001 형식으로 갱신
            self.update_version_status(row, combo, self.table.item(row, 3))  # UI 갱신
            self.table.item(row, 3).setText(f"🟢 .v{new_version:03d}")  # 최신 버전 컬럼 갱신

    def onCellClicked(self, row, column):
        """ 테이블에서 Asset 클릭 시 Maya에서 해당 오브젝트 선택"""
        if column == 1:  # "Asset" 열을 클릭했을 때
            asset_name = self.table.item(row, 1).text()  # 해당 에셋 이름 가져오기
            MayaReferenceManager.select_asset_by_name(asset_name)  # 해당 이름으로 Maya에서 오브젝트 선택
            
    def update_maya_reference(self, row, new_version):
        """Maya에서 참조된 파일을 새로운 버전으로 업데이트"""
        references = cmds.file(q=True, reference=True) or []

        if row >= len(references):
            print(f"참조 파일을 찾을 수 없음: {row}")
            return
        # 🔹 현재 참조된 파일 경로 가져오기
        ref_path = cmds.referenceQuery(references[row], filename=True, withoutCopyNumber=True)
        print(f"안녕 난느 {ref_path}")
        
        if not ref_path or not os.path.exists(ref_path):
            print(f"⚠️ 참조 경로를 찾을 수 없습니다: {ref_path}")
            return

        # 참조된 파일이 존재하는 디렉토리 가져오기
        asset_dir = os.path.dirname(ref_path)
        
        # 파일 이름에서 버전 정보 제거
        base_name, ext = os.path.splitext(os.path.basename(ref_path))
        base_name_no_version = re.sub(r"\.v\d{3}", "", base_name)  # `v001` 같은 버전 제거

        # 파일 확장자를 확실하게 설정하기
        try :
            file_extension = '.ma'
        except:
            file_extension = '.mb'
    
        # 선택된 버전으로 파일명 갱신
        new_filename = f"{base_name_no_version}{new_version}{file_extension}"  # 새 파일명 생성

        #  해당 디렉토리 내에서 선택된 버전 찾기
        latest_path = os.path.join(asset_dir, new_filename)
        print(f" 자 업뎃 드가자{latest_path}") 

        if not os.path.exists(latest_path):
            print(f"{new_filename} 파일이 존재하지 않습니다.")
            return
        # 참조 파일을 언로드하고, 새 버전으로 로드
        try:
            # 참조 노드 가져오기
            ref_node = cmds.referenceQuery(references[row], referenceNode=True)
            # 기존 참조를 언로드
            cmds.file(unloadReference=ref_node)
            # 새 버전 파일 로드
            cmds.file(latest_path, loadReference=ref_node, force=True)
            print(f" 참조 업데이트 완료: {ref_path} → {latest_path}")
        except Exception as e:
            print(f" 참조 업데이트 실패: {e}")

