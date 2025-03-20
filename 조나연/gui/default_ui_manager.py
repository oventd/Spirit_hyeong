try:
    from PySide6.QtGui import QPixmap
except:
    from PySide2.QtGui import QPixmap

import sys
import os

current_file_path = os.path.abspath(__file__)
na_spirit_dir = os.path.abspath(os.path.join(current_file_path, "../../"))
for root, dirs, files in os.walk(na_spirit_dir):
    if '__pycache__' not in root: 
        sys.path.append(root)

sys.path.append("/home/rapa/NA_Spirit/upload/") 
from asset_upload_manager import AssetUploadManager
from constant import *
from tree_ui_manager import TreeUiManager
from table_ui_manager import TableUiManager
from like_state import LikeState
from ui_loader import UILoader  


class DefaultUiManager:
    _instance = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultUiManager, cls).__new__(cls)

        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"): 
            super().__init__()
            ui_loader = UILoader("/home/rapa/NA_Spirit/gui/asset_main2.ui")
            self.ui = ui_loader.load_ui()
            self.ui.show()
            self.main_ui_setting()
            self._initialized = True  

    def set_search_area_design(self):
        """
        검색창의 디자인 요소를 삽입하는 메서드
        """
        search_input =self. ui.search
        search_input.setPlaceholderText("검색하기") 
        search_input.setStyleSheet("""
        QLineEdit {
            border: none;                  /* 테두리 제거 */
            background: transparent;       /* 배경을 투명으로 설정 */
            color: white;                  /* 글자 색상을 흰색으로 설정 */
            font-family: 'Pretendard';     /* 폰트는 Pretendard로 설정 */
            font-weight: light;            /* 폰트 두께를 light로 설정 */
            font-size: 13px;               /* 폰트 크기는 11px */
        }
    """)
        
    def main_ui_setting(self):

        """
        첫화면의 디자인적 요소를 정해주는 메서드
        """
        self.ui.like_download_btn.hide()
        self.ui.like_download_btn_area.hide()
        self.sub_bar = False
        self.ui.comboBox.setStyleSheet("""
            QComboBox {
                background-color: #121212;
                color: white;
                border: 1px solid #303030;
                border-radius: 8px; 
            }

            QComboBox QAbstractItemView {
                background-color: black;  /*  드롭다운 배경을 검은색으로 설정 */
                color: #707070;  /* 글씨 색을 흰색으로 설정 */
                selection-background-color: gray;  /* 선택된 항목의 배경을 회색으로 설정 */
                selection-color: white;  /*  선택된 항목의 글씨 색 */
                border: 1px solid #303030;;
            }
        """)
        self.user_num()
        TreeUiManager.tree_widget()
        TableUiManager().update_table(None,UPDATED_AT, 50, 0,None)
        self.set_search_area_design()
        self.ui.like_empty_notice.hide()
        self.ui.like_btn.setIcon(LikeState().like_icon_empty)
        self.like_active = False
        info_list_bar_s=QPixmap("/nas/spirit/asset_project/source/info_list_bar.png")
        self.ui.info_list_bar_s.setPixmap(info_list_bar_s)
        self.ui.toggle_btn.setPixmap(LikeState().toggle_open) 
        bg =QPixmap("/nas/spirit/asset_project/source/bg.png")
        self.ui.label.setPixmap(bg)
        self.ui.stackedWidget.hide()
        self.ui.depth_label.hide()
        self.ui.stackedWidget_2.removeWidget(self.ui.page)
        self.ui.stackedWidget_2.removeWidget(self.ui.page_2)
        
    def user_num(self):
        sg_user_name = AssetUploadManager()
        name = sg_user_name.get_user_name()
        self.ui.user_num.setText(name)

