import sys, os
try:
    from PySide6.QtWidgets import QListWidgetItem
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap
except:
    from PySide2.QtWidgets import QListWidgetItem
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QPixmap

from ui_loader import UILoader  
current_file_path = os.path.abspath(__file__)
na_spirit_dir = os.path.abspath(os.path.join(current_file_path, "../../"))

for root, dirs, files in os.walk(na_spirit_dir):
    if '__pycache__' not in root: 
        sys.path.append(root)
   
sys.path.append("/home/rapa/NA_Spirit/upload")
from constant import *
from logger import *
from like_state import LikeState
from asset import Asset
from assetmanager import AssetService
from send_asset_flow import SendAssetFlow
from asset_download_manager import AssetDownloadManager
import sgtk

class DownloadManager:
    
    _instance = None  
    

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DownloadManager, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # 중복 초기화를 방지
            super().__init__()
            self.asset = Asset()
            self.exemples = []
            self.download_list_asset ={}
            self.like_state = LikeState()
            self.sender=SendAssetFlow()
            ui_loader = UILoader("/home/rapa/NA_Spirit/gui/asset_main2.ui")
            self.ui = ui_loader.load_ui()
            self.ui.show()
            self.ui.download_format_touch_area.clicked.connect(self.set_download_format_all)
            self.ui.exit_btn_2.clicked.connect(self.exit_sub_bar_all)
            self.ui.download_touch_area.clicked.connect(self.download_all)
            self.ui.download_listwidget.clear()
            self.ref_download_toggle_pixmap = QPixmap("/nas/spirit/asset_project/source/popup_source/reference_toggle.png")
            self.import_download_toggle_pixmap = QPixmap("/nas/spirit/asset_project/source/popup_source/import_toggle.png")
            self.ui.download_format_label.setPixmap(self.ref_download_toggle_pixmap)
            self.setDownloadFormat = False  #False가 레퍼런스
            self.logger = create_logger(UX_DOWNLOAD_LOGGER_NAME, UX_DOWNLOAD_LOGGER_DIR)
            self.engine = sgtk.platform.current_engine()  # ShotGrid Toolkit 엔진 가져오기
            self.context = self.engine.context  # 컨텍스트 가져오기
    def download_likged_assets_all(self):
        """
        다운로드 리스트를 하트 누른 리스트에서 가져온 뒤 
        에셋정보 추출하고 다음 메서드로 넘져주는 메서드
        """

        self.ui.download_listwidget.clear()
        self.exemples = self.like_state.like_asset_list
        self.download_list_asset=AssetService.get_assets_by_ids(self.exemples)
        self.add_list_widget(self.download_list_asset)
        self.ui.stackedWidget.show()
        self.ui.depth_label.show()
        self.ui.stackedWidget.setCurrentIndex(1)


    def download_likged_assets(self):
        """
        선택한 자산을 다운로드 목록에 추가하고, 관련 UI 요소를 업데이트합
        """
        self.ui.download_listwidget.clear()
        self.ui.stackedWidget.show()
        self.ui.depth_label.show()
        self.ui.stackedWidget.setCurrentIndex(1)
        self.download_list_asset = {self.asset.current["name"]: str(self.asset.current["_id"])}
        self.add_list_widget(self.download_list_asset)


    def exit_sub_bar_all(self):
        """
        다운로드 화면을 닫고 기본 화면으로 복귀
        """
        self.ui.stackedWidget.hide()
        self.ui.depth_label.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def set_download_format_all(self):
        """다운로드 방식을 변경하는 토글 기능을 수행"""
        if self.setDownloadFormat == False:
            self.setDownloadFormat = True 
            self.ui.download_format_label.setPixmap(self.import_download_toggle_pixmap)
        else:
            self.setDownloadFormat = False
            self.ui.download_format_label.setPixmap(self.ref_download_toggle_pixmap)

    def add_list_widget(self,asset):
        """동적으로 리스트 위젯의 항목을 추가하는 메서드"""

        for item_text in asset:
            item = QListWidgetItem(item_text)  # 항목 생성
            item.setCheckState(Qt.Checked)  # 체크박스를 체크된 상태로 설정
            self.ui.download_listwidget.addItem(item) 
        self.list_widget_stylesheet()
        

    def list_widget_stylesheet(self):
        """다운로드 리스트 위젯의 스타일을 설정합니다."""

        self.ui.download_listwidget.setStyleSheet("""
            QListWidget {
                background-color: #222222;  /* 리스트의 배경을 투명하게 설정 */
                color:#ffffff;
            }

            QListWidget::item:checked::indicator {
            
                border-radius: 50%;  /* 체크박스를 원형으로 설정 */
                width: 16px;  /* 체크박스 크기 설정 */
                height: 24px;
            }

            QListWidget::item:unchecked::indicator {
             
                border: 0.4px solid #202020;  /* 체크박스의 테두리 색상 */
                border-radius: 50%;  /* 체크박스를 원형으로 설정 */
                width: 16px;  /* 체크박스 크기 설정 */
                height: 24px;
            }
        """)
            
            
    def download_all(self):
        """
        체크된 아이템을 기준으로 다운로드 또는 임포트 수행
        """
        # 체크된 아이템 리스트 추출
        download_fix_list = []
        for i in range(self.ui.download_listwidget.count()):
            item = self.ui.download_listwidget.item(i)
            if item.checkState() == Qt.Checked:
                download_fix_list.append(item.text())

        # 체크된 아이템에 대응하는 ID 리스트 추출
        selected_ids_list = [self.download_list_asset[name] for name in download_fix_list if name in self.download_list_asset]

        # 리스트 출력
        print(f"다운로드 픽스 리스트: {download_fix_list}")
        print(f"셀렉트 아이디 리스트: {selected_ids_list}")

        # 아무것도 체크되지 않았으면 함수 종료
        if not selected_ids_list:
            print("체크된 항목이 없어 다운로드를 수행하지 않습니다.")
            return

        # 다운로드 방식에 따라 다르게 처리
        if not self.setDownloadFormat:
            format = 'Reference'
            print(f"{selected_ids_list}이(가) {format}로 다운로드되었습니다")
            self.sender.redata_for_flow(selected_ids_list)

            assets=AssetService().get_assets_by_ids_all_return(selected_ids_list)
            for asset in assets:
                category = asset["category"]
                source_path = asset["source_url"]
                print(category, source_path)
                AssetDownloadManager(self.context).process(category,source_path)
        else:
            format = 'Import'
            print(f"{selected_ids_list}이(가) {format}로 다운로드되었습니다")
            self.sender.redata_for_flow(selected_ids_list)

    def on_button_click(self):
        # 버튼 클릭 시 입력된 값을 MainWindow로 전달하는 시그널 발생
        value = self.ui.lineEdit.text()  # 입력된 텍스트 가져오기

download = DownloadManager()
download.download_all()