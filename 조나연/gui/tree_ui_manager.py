from PySide6.QtCore import Qt
import sys
import os

current_file_path = os.path.abspath(__file__)
na_spirit_dir = os.path.abspath(os.path.join(current_file_path, "../../"))
for root, dirs, files in os.walk(na_spirit_dir):
    if '__pycache__' not in root: 
        sys.path.append(root)

from PySide6.QtCore import Qt
from constant import *

from check import Check
from table_ui_manager import TableUiManager
from ui_loader import UILoader

class TreeUiManager:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TreeUiManager, cls).__new__(cls)

        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):  
            ui_loader = UILoader("/home/rapa/NA_Spirit/gui/asset_main2.ui")
            self.ui = ui_loader.load_ui()
            self.ui.show()
            
            self.ui.treeWidget.itemClicked.connect(self.toggle_checkbox)
            self.ui.treeWidget.itemClicked.connect(self.get_checked_items)


    def get_checked_items(self):
        """QTreeWidget에서 체크된 항목들의 텍스트를 가져오는 함수"""
        checked_items = []  # 체크된 항목을 저장할 리스트
        root = self.ui.treeWidget.invisibleRootItem()  # 트리의 루트 아이템 가져오기

        def traverse_tree(item):
            """재귀적으로 트리의 모든 항목을 탐색"""
            for i in range(item.childCount()):
                child = item.child(i)
                if child.checkState(0) == Qt.Checked:  #  체크된 항목 확인
                    checked_items.append(child.text(0))  #  항목의 텍스트 저장
                traverse_tree(child)  #  자식 항목이 있을 경우 재귀적으로 탐색

        traverse_tree(root)  # 트리 탐색 시작

        Check.checked_items = checked_items
        return checked_items
        

    @staticmethod
    def tree_widget():
        """
        트리 위젯 스타일 시트 설정
        """
        ui_loader = UILoader("/home/rapa/NA_Spirit/gui/asset_main2.ui")
        ui = ui_loader.load_ui()
        ui.show()
        ui.treeWidget.setStyleSheet("""
            QTreeWidget::item {
                color: white;
                padding: 10px;  /* 항목 간 간격을 조절 */
            }
            QTreeWidget {background: transparent;  /*배경색을 투명하게 설정*/
            }
            """)
        ui.treeWidget.expandAll()
        root = ui.treeWidget.invisibleRootItem()  # 트리 위젯의 최상위 항목(root item)을 반환하는 treeWidget 객체의 메서드

        for i in range(root.childCount()):  # 최상위 항목의 자식 갯수를 가져오는 메서드
            parent = root.child(i)   
  
            # print(parent.text(0))  #열과 행이 존재하기 때문에 지정을 해줘야 출력이 가능
            for j in range(parent.childCount()):  # 부모의 자식 항목(Child)
                child = parent.child(j)
                # print(child.text(0))
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)  # 체크박스를 만들수 있는 QT 기능 플래그를 child의 플래그에 추가
                child.setCheckState(0, Qt.Unchecked) #

    def toggle_checkbox(self, item, column): 
        """트리 항목 클릭 시 체크 상태 토글"""
        if item.flags() & Qt.ItemIsUserCheckable:  # item이 체크 가능 여부 확인
            self.ui.tableWidget.clear()
            current_state = item.checkState(column)  #item.checkState(column)은 현재 열(column)에 있는 체크 상태를 가져오는 메서드
            new_state = Qt.Checked if current_state == Qt.Unchecked else Qt.Unchecked #체크되어있다면 미체크로, 미체크라면 체크로 상태 변경 

            filter_name_convert =str(item.text(0)) 
            
            #체크박스의 item 문자열을 상수화 시키기
            parent_name = item.parent()
            parent_item_convert=parent_name.text(0)

            #체크박스의 parent 문자열을 db의 key 명과 일치 시키기
            if parent_item_convert == "Asset":
                parent_item_convert = "asset_type"
            elif parent_item_convert == "Category":
                parent_item_convert = "category"
            else: 
                parent_item_convert = "style"

            item.setCheckState(column, new_state)  # 체크박스 상태 변경
            
            if new_state == Qt.Checked:  #체크 상태일 경우 부모 item을 키로 item을 list에 담아 value로 추가
                Check().dict.setdefault(parent_item_convert, []).append(filter_name_convert)
            else:  #체크 해제 상태일 경우 부모 item의 키에서 해당하는 value 삭제
                Check().dict[parent_item_convert].remove(filter_name_convert)
                if Check().dict[parent_item_convert] == []:
                    del Check().dict[parent_item_convert]
        
            sort_by = self.ui.comboBox.currentText()
            if sort_by == "최신 순":
                sort_by=CREATED_AT
            elif sort_by == "다운로드 순":
                sort_by = DOWNLOADS
            else:
                sort_by = UPDATED_AT
                
            TableUiManager().update_table( sort_by= sort_by, skip = 0, fields =None)

        
