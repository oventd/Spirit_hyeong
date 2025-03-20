try:
    from PySide6.QtWidgets import QLabel
    from PySide6.QtCore import Signal, Qt
except:
    from PySide2.QtWidgets import QLabel
    from PySide2.QtCore import Signal, Qt

from constant import *
from db_crud import AssetDb  
from ui_loader import UILoader


class ClickableLabel(QLabel):
    clicked = Signal() 

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        """라벨에 클릭 시그널을 넣어주는 메서드"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  


class AssetService:
    """
    UI와 DB 사이의 중간 계층 역할을 수행하는 서비스 클래스.
    - UI에서는 직접 db_crud.py를 호출하지 않고, 이 클래스를 통해서만 데이터 요청을 함.
    """
    @staticmethod
    def get_assets_by_ids(ids_list):
        """
        여기서 리스트를 받아 에셋으로 변환하고 해당 내용을 id: name 형식으로 변환하는 메서드 
        """

        asset_manager = AssetDb()  
        dowmload_list_asset= asset_manager.find(filter_conditions = ids_list)  # 자산 삭제
        
        asset_dict = {asset["name"] : str(asset["_id"]) for asset in dowmload_list_asset}
        return asset_dict
    
    @staticmethod
    def get_assets_by_ids_all_return(ids_list):
        """
        리스트를 매개변수로 받아서 에셋의 모든 필드를 담아서 리턴하는 메서드
        """

        asset_manager = AssetDb() 
        dowmload_list_asset= asset_manager.find(filter_conditions = ids_list) 
        
       
        return dowmload_list_asset
                
                

    @staticmethod
    def get_all_assets(filter_conditions, sort_by, limit, skip,user_query): 
        """
        모든 자산 데이터를 MongoDB에서 가져옴. 무한 스크롤을 지원.
        - db_crud.py의 find() 호출
        - 데이터를 UI에서 쉽게 사용 가능하도록 리스트로 변환
        :param filter_conditions: 필터 조건 (기본값은 None, 모든 자산 조회)
        :param sort_by: 정렬 기준 (기본값은 None, 정렬하지 않음)
        :param limit: 조회할 데이터 수 (기본값은 5)
        :param skip: 건너뛸 데이터 수 (기본값은 0, 첫 번째 페이지)
        :return: 조회된 자산 리스트
        """   
        return AssetDb().search(filter_conditions=filter_conditions, sort_by=sort_by, limit=limit, skip=skip,user_query = user_query)
        
    @staticmethod
    def search_input(search_word, filter_conditions):
        """
        데이터를 검색합니다.
        :param user_query: 검색어
        :param fields: 검색 결과에서 가져올 필드 목록
        :return: 검색 결과
        """
        return AssetDb().search(user_query=search_word, filter_conditions = filter_conditions) 
    
    @staticmethod
    def get_asset_by_id_all(filter_conditions, sort_by=None, limit=None, skip=None, user_quaery = None):
        return AssetDb().search(user_quaery ,filter_conditions=filter_conditions, sort_by=sort_by, limit=limit, skip=skip)
    
            
    @staticmethod
    def get_asset_by_id(asset_id):
        """
        특정 ID의 자산 데이터를 가져옴.
        - UI에서 사용자가 클릭한 자산의 ID를 전달받아 해당 데이터를 조회
        """
        return AssetDb().find_one(asset_id)
    
    @staticmethod
    def upsert_data(asset_data):
        """
        새로운 자산 데이터를 새로 생성하고, 
        있은 경우 업데이트하여 DB에 추가합니다.
        :param asset_data: 자산 데이터
        :return: 추가된 자산의 ID
        """
        return AssetDb().upsert_asset(asset_data)  # 자산 데이터를 DB에 삽입
    
    @staticmethod
    def update_count(asset_id):
        """
        자산 데이터를 업데이트
        :param asset_id: 수정할 자산 ID
        :param update_data: 수정할 데이터
        :return: 업데이트 성공 여부
        """
        return AssetDb().increment_count(asset_id)  # 자산 데이터 업데이트
    
    @staticmethod
    def delete_asset(asset_id):
        """
        자산 데이터를 삭제
        :param asset_id: 삭제할 자산 ID
        :return: 삭제 성공 여부
        """
        return AssetDb().delete_one(asset_id)  # 자산 삭제