from PySide6.QtWidgets import  QLabel, QWidget
from PySide6.QtCore import  Qt
from PySide6.QtGui import QPixmap, QPixmap
from PySide6.QtWidgets import QSizePolicy ,QVBoxLayout
from PySide6.QtMultimediaWidgets import QVideoWidget
from functools import partial
import sys
import os
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui_loader import UILoader   

current_file_path = os.path.abspath(__file__)
na_spirit_dir = os.path.abspath(os.path.join(current_file_path, "../../"))
for root, dirs, files in os.walk(na_spirit_dir):
    if '__pycache__' not in root: 
        sys.path.append(root)

from assetmanager import AssetService  
from assetmanager import ClickableLabel
from PySide6.QtCore import Qt
from constant import *
from like_state import LikeState
from asset import Asset
from check import Check
from subwin import SubWin
from dynamic_circle_label import DynamicCircleLabel
from logger import *
from download_manager import DownloadManager
from json_manager import DictManager
from ui_loader import UILoader   


class TableUiManager:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TableUiManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # 중복 초기화를 방지
            super().__init__()
            ui_loader = UILoader("/home/rapa/NA_Spirit/gui/asset_main2.ui")
            self.ui = ui_loader.load_ui()
            self.ui.show()
            self.ui.comboBox.currentTextChanged.connect(self.set_sorting_option)
            self._initialized = True  # 인스턴스가 초기화되었음을 표시
            self.search_word =None
            self.ui.exit_btn.clicked.connect(self.exit_sub_win)
            self.ui.image_l_btn.clicked.connect(partial (SubWin.prev_slide, self.ui.stackedWidget_2))
            self.ui.image_r_btn.clicked.connect(partial (SubWin.next_slide, self.ui.stackedWidget_2))
            self.ui.toggle_btn_touch_area.clicked.connect(self.toggle_change) # 토글 버튼 토글 이벤트
            self.ui.like_btn.clicked.connect(self.toggle_like_icon)
            self.ui.search.textEdited.connect(self.search_input)
            download_manager=DownloadManager()
            self.asset_manager = Asset()
            self.like_state = LikeState()
            self.like_state.like_asset_list = DictManager.load_dict_from_json()
            self.ui.like_download_btn_area.clicked.connect(download_manager.download_likged_assets_all)
            self.ui.download_btn.clicked.connect(download_manager.download_likged_assets)
            self.logger = create_logger(UX_Like_ASSET_LOGGER_NAME, UX_Like_ASSET_LOGGER_DIR)
            self.asset_dict = {}
        
    def search_input(self, search_word):
        """검색할 단어 검색 후 업데이트 테이블 실행 메서드"""
        self.search_word = search_word
        self.update_table()


    def remove_lable(self):

        """동적으로 만들어진 라벨을 삭제하는 메서드"""
        
        while self.ui.image_widget_s.count() > 0:
            item = self.ui.image_widget_s.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # QLabel 메모리 해제

      
        for label in self.ui.stackedWidget_2.findChildren(QLabel):
            label.deleteLater()

        while self.ui.image_widget_s.count() > 0:
            item = self.ui.image_widget_s.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label in self.ui.stackedWidget_2.findChildren(QLabel):
            label.deleteLater()

        for video_widget in self.ui.stackedWidget_2.findChildren(QVideoWidget):
            video_widget.deleteLater()

        self.video_widgets = []
        self.video_players = []

    def make_label_list(self, list_len): 
        """미리보기 이미지를 담는 라벨을 만드는 메서드"""
        self.remove_lable()
        self.make_labels = []  # 리스트 초기화

        for _ in range(list_len):  
            label = QLabel()
            label.setFixedSize(60, 60)
            label.setAlignment(Qt.AlignCenter)
            self.ui.image_widget_s.addWidget(label)  
            self.make_labels.append(label)

    def set_sorting_option(self, option):
        """
        유저가 설정한 sorting_option에 맞게 table에 적절한 인자를 전달하여 
        테이블 위젯의 나열순서를 정하는 메서드
        """

        if option == "오래된 순":
            print(f"오래된 순의 필터임 :{Check().dict}")
            self.update_table(None, CREATED_AT, 0,None)

        elif option =="다운로드 순":
            print("다운로드된 순서를 정렬할게요")
            self.update_table(None, DOWNLOADS, 0,None)

        else:
            print("최신 순서를 정렬할게요")
            self.update_table(None, UPDATED_AT, 0, None)
        
        
    
    def update_table(self, filter_conditions=None, sort_by=None, limit=None, skip=0, fields=None):
        """테이블을 재 로드할 때 사용하는 메서드"""
      
        self.ui.like_empty_notice.hide()  
        search_word = self.search_word
        if self.search_word is not None:
            if len(self.search_word) < 3:
                search_word =None
        filter_conditions = {}
        if LikeState().state:
            filter_conditions[OBJECT_ID] = LikeState().like_filter_condition[OBJECT_ID]
        if Check().dict:
            for key, value in Check().dict.items():
                filter_conditions[key] = value     

        assets  = list(AssetService.get_all_assets(filter_conditions, sort_by, limit, skip,search_word)) 
        self.ui.tableWidget.clear()
        self.make_table(assets)

        filter_conditions = None
    
    def make_table(self, assets):
        """테이블을 동적으로 열과 행을 만드는 메서드"""
     
        len_asset =len(assets)
        self.ui.tableWidget.horizontalHeader().setVisible(False)  # 열(가로) 헤더 숨기기
        self.ui.tableWidget.verticalHeader().setVisible(False)  # 행(세로) 헤더 숨기기

        max_columns = 5  # 한 줄에 최대 5개 배치

        rows = (len_asset / max_columns +1)   # 행 개수 계산

        self.ui.tableWidget.setRowCount(rows)  # 행 개수 설정
        self.ui.tableWidget.setColumnCount(max_columns)  # 열 개수 설정
        


        for index, asset in enumerate(assets):
            row_index = index // max_columns  # index 항목이 몇 번째 행(row)에 있는 정의
            col_index = index % max_columns   # 나머지를 통해 몇번째 열에 있는지 정의
            self.add_thumbnail(row_index, col_index, asset)
        

    def add_thumbnail(self, row, col, asset):

        """썸네일 이미지용으로 클릭 가능한 라벨을 만들고
            이를 함수와 클릭시 연결되게 만들기 """

        thumbnail_path = asset["preview_url"]
        asset_name = asset["name"] 
        aseet_type = asset["asset_type"]

        widget = QWidget()  # 셀 안에 넣을 위젯 생성
        layout = QVBoxLayout()  # 세로 정렬을 위한 레이아웃 생성
        layout.setContentsMargins(0, 0, 0, 10)  # 여백 제거
        layout.setAlignment(Qt.AlignTop)


        Thum = ClickableLabel("썸네일", parent=widget)
        name = ClickableLabel("이름", parent=widget)
        type = ClickableLabel("타입", parent=widget)

        Thum.clicked.connect(lambda: self.set_detail_info(asset))
        name.clicked.connect(lambda: self.set_detail_info(asset))
        type.clicked.connect(lambda: self.set_detail_info(asset))

        layout.addWidget(Thum)
        layout.addWidget(name)
        layout.addWidget(type)

        widget.setLayout(layout)  # 위젯에 레이아웃 설정
        

        pixmap = QPixmap(thumbnail_path)
        if pixmap.isNull():
            print(f" 이미지 로드 실패: {thumbnail_path}")

        Thum.setPixmap(pixmap)
        Thum.setFixedHeight(160)
        
        Thum.setAlignment(Qt.AlignCenter)

        name.setText(asset_name)
        name.setAlignment(Qt.AlignCenter)
        type.setText(aseet_type)

        name.setStyleSheet("""
            color: white;                 /* 글자 색상 */
            font-family: 'Pretendard';          /* 글꼴 */
            font-size: 14px;              /* 글자 크기 */
            font-weight: Thin;            /* 글자 굵기 */
        """)

        name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        name.setFixedHeight(14)
        name.setAlignment(Qt.AlignCenter)

        type.setStyleSheet("color: white;")
        type.setStyleSheet("""
            color: white;                 /* 글자 색상 */
            font-family: 'Pretendard';          /* 글꼴 */
            font-size: 12px;              /* 글자 크기 */
            font-weight: Pretendard-ExtraLight;            /* 글자 굵기 */
        """)
        type.setAlignment(Qt.AlignCenter)
        
        type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        type.setFixedHeight(18)

        self.ui.tableWidget.setCellWidget(row, col, widget)  # 행과 열에 이미지 추가
        self.ui.tableWidget.resizeRowsToContents() 
      


    def exit_sub_win(self):
        self.ui.stackedWidget.hide()
        self.ui.depth_label.hide()
        self.update_like_count()

    def set_detail_info(self, asset):
        Asset().current = asset
        ui=self.ui
        ui.stackedWidget.show()
        ui.depth_label.show()
        detail_thum_urls=[]
        
        try:
            self.timer.stop()
        except:
            pass
        

        LikeState().set_like_icon(str(asset[OBJECT_ID]),self.ui.like_btn)
        
        Asset().current= asset
        ui.info_name.setText(asset[NAME])
        ui.info_name_2.setText(asset[NAME])
        ui.description.setText(asset[DESCRIPTION])
        ui.asset_type.setText(f"에셋 타입 : {asset[ASSET_TYPE]}")
        ui.resolution.setText(f"해상도 : {asset[RESOLUTION]}")
        ui.downloads.setText(f"다운로드 횟수 : {asset[DOWNLOADS]}회")
        ui.create_at.setText(f"최초 생성일 : {asset[CREATED_AT]}회")
        ui.update_up.setText(f"최종 수정일 : {asset[UPDATED_AT]}회")
        ui.creator.setText(f"담당 직원 : {asset[CREATOR_NAME]} ( ID : {asset[CREATOR_ID]} )")

        #세부항목 태그
        common_style = "color: #ffffff; background-color: #282828; padding: 5px; border-radius: 12px;"

        # QLabel 목록과 해당할 데이터 매핑
        labels = {
            ui.category: asset[CATEGORY],
            ui.style_area: asset[STYLE],
            ui.license_type: asset[LICENSE_TYPE],
        }

        # 반복문을 사용해 설정 적용
        for label, text in labels.items():
            label.setText(text)
            label.setStyleSheet(common_style)
            label.adjustSize()

        # 이미지 URL 가져오기
        if asset[ASSET_TYPE]=="Texture":

            for url in asset["image_url"]:
                detail_thum_urls.append(url)


        elif asset[ASSET_TYPE]=="3D Model":
            for url in asset["video_url"]:
                detail_thum_urls.append(url)
            
        elif asset[ASSET_TYPE]=="HDRI":
            for url in asset["image_url"]:
                detail_thum_urls.append(url)
        else:
            for url in asset["image_url"]:
                detail_thum_urls.append(url)

        self.make_label_list(len(detail_thum_urls))
        SubWin.show_asset_detail_image(self.ui.stackedWidget_2,detail_thum_urls, self.make_labels)



            
    def toggle_like_icon(self):
       
        """하트 버튼을 누르는 시그널로 실행
        아이콘 변경 & 딕셔너리에 좋아요한 asset 정보 저장 """

        asset = Asset().current
        asset_object_id = str(asset[OBJECT_ID])
        current_icon = self.ui.like_btn.icon()
     
        if current_icon.cacheKey() == self.like_state.like_icon_empty.cacheKey():  #빈하트 상태일때 
            self.ui.like_btn.setIcon(self.like_state.like_icon)
            self.like_state.like_asset_list.append(asset_object_id)
            
            self.logger.info(f"유저가 {asset[NAME]} 에셋을 관심리스트에 추가했습니다\n해당 에셋 정보 : {asset}")
            DictManager().save_dict_to_json(self.like_state.like_asset_list)
     

            if LikeState().state == True:
                print("저 서브바가 열려있을때만 닫혀요")
                self.ui.tableWidget.clear()
                self.update_table(sort_by=UPDATED_AT, limit=0, skip=0,fields=None)
                self.ui.like_download_btn.show()
                self.ui.like_download_btn_area.show()

        
        else:  # 채워진 하트 상태일 때 (좋아요 취소)
            print("하트 지워짐")
            self.ui.like_btn.setIcon(self.like_state.like_icon_empty)  # 빈 하트로 변경
            if asset_object_id in self.like_state.like_asset_list:
                index = self.like_state.like_asset_list.index(asset_object_id)
                remove_asset=self.like_state.like_asset_list.pop(index)  # 리스트에서 제거
                self.logger.info(f"유저가 {asset[NAME]} 에셋을 관심리스트에서 삭제했습니다\n해당 에셋 정보 : {remove_asset}")
                print(f"유저가 {asset[NAME]} 에셋을 관심리스트에서 삭제했습니다\n해당 에셋 정보 : {remove_asset}")
                DictManager().save_dict_to_json(self.like_state.like_asset_list)

            if LikeState().state == True:
                print("저 서브바가 열려있을때만 닫혀요")
                self.ui.tableWidget.clear()
                self.update_table(sort_by=UPDATED_AT, limit=0, skip=0,fields=None)
                self.ui.like_download_btn.show()
                self.ui.like_download_btn_area.show()
          
                
                
        self.like_state.set_like_icon(asset_object_id, self.ui.like_btn)

    def toggle_change(self): 
        """토글 버튼 변경 이벤트 - 내부 위젯도 삭제"""

        #  기존 위젯 삭제 (내부 요소 포함)
        self.clear_layout(self.ui.like_asset_number)

        if LikeState().state == False:
            self.ui.toggle_btn.setPixmap(LikeState().toggle_like)
            
            LikeState().state = True
            if not LikeState().like_asset_list:
                self.ui.tableWidget.clear()
                self.ui.like_empty_notice.show()
                
            else:
                self.ui.tableWidget.clear()
                self.update_table(sort_by=UPDATED_AT, limit=0, skip=0,fields=None)
                self.ui.like_download_btn.show()
                self.ui.like_download_btn_area.show()

                # 새로운 DynamicCircleLabel 추가
                self.label = DynamicCircleLabel("")
                self.ui.like_asset_number.addWidget(self.label)  #  새로운 라벨 추가
                self.update_like_count()
                
                self.ui.like_download_btn.setPixmap(LikeState().like_download_image)

                self.ui.like_empty_notice.hide()
        else: 
            self.ui.like_download_btn.hide()
            self.ui.like_download_btn_area.hide()
            if LikeState().state == True:
                self.ui.toggle_btn.setPixmap(LikeState().toggle_open)
                LikeState().state = False
                self.ui.like_empty_notice.hide()
                self.ui.tableWidget.clear()
                self.update_table(sort_by=UPDATED_AT, limit=0, skip=0,fields=None)
                #사용자 pc에 저장해두고 라이크 받을때 마다 오브젝트 id를 json에 저장해두고 

    def update_like_count(self):
        """ 기존 라벨을 유지하면서 숫자만 변경"""
        like_count = len(LikeState().like_asset_list)
        self.label.setText(str(like_count))  #  기존 라벨의 텍스트만 변경
        self.label.update_size()  #  크기 업데이트 (동적으로 적용)

    def remove_widget_with_children(self,widget):
        """위젯과 그 내부 요소 삭제"""
        if widget is not None:
            layout = widget.layout()  #  위젯에 레이아웃이 있는 경우 가져오기
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    child_widget = item.widget()
                    if child_widget:
                        child_widget.deleteLater()  #  내부 요소 삭제
            widget.setParent(None)  #  부모에서 제거
            widget.deleteLater()  # 위젯 자체도 삭제

    def clear_layout(self, layout):
        """레이아웃 내부의 모든 요소 삭제"""
        while layout.count():  # 레이아웃에 위젯이 남아있는 동안 반복
            item = layout.takeAt(0)  # 첫 번째 아이템 가져오기
            widget = item.widget()  # 아이템이 위젯인지 확인
            if widget is not None:
                widget.setParent(None)  #  부모에서 제거
                widget.deleteLater()  #  메모리에서 완전 삭제


    