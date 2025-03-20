try:
    from PySide6.QtGui import QPixmap, QIcon
except:
    from PySide2.QtGui import QPixmap, QIcon

from bson import ObjectId

class LikeState:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # 올바른 싱글톤 생성
        return cls._instance  # 기존 인스턴스 반환

    def __init__(self):
        if hasattr(self, "_initialized"):  # 중복 초기화를 방지
            return
        self._state = False  # 실제 값을 저장하는 비공개 속성

        self._toggle_like = QPixmap("/nas/spirit/asset_project/source/toggle_like.png")
        self._toggle_open =QPixmap("/nas/spirit/asset_project/source/toggle_open.png")
        self._like_download_image = QPixmap("/nas/spirit/asset_project/source/download_btn.png")
        self._like_icon_empty = QIcon("/nas/spirit/asset_project/source/like_icon.png")
        self._like_icon = QIcon("/nas/spirit/asset_project/source/like_icon_on.png")
        self._initialized = True
        self._like_asset_list = []
        self._like_count = len(self._like_asset_list)

    @property
    def state(self):
        return self._state  # _state 값을 반환

    @state.setter
    def state(self, value):
        self._state = value  # _state 값을 변경
    @property
    def toggle_like(self):
        return self._toggle_like
    
    @property
    def toggle_open(self):
        return self._toggle_open

    @property
    def like_asset_list(self):
        return self._like_asset_list
    
    @like_asset_list.setter
    def like_asset_list(self, value):
        self._like_asset_list = value

    @property
    def like_icon_empty(self):
        return self._like_icon_empty

    @property
    def like_icon(self):
        return self._like_icon
    
    @property
    def like_download_image(self):
        return self._like_download_image
    
    @property
    def like_filter_condition(self):
        result = {'_id':[]}
        for obj_id in self._like_asset_list:
            result['_id'].append(ObjectId(obj_id))
        return result
    
    @property
    def like_count(self):
        return self._like_count
    
    @like_count.setter
    def like_count(self, value):
        self._like_count = value
    

    
    def set_like_icon(self, asset_object_id:str, like_btn):
        if asset_object_id in self.like_asset_list: #에셋딕트 안에 에셋이 있다면 
            like_btn.setIcon(self.like_icon)
        else:
            like_btn.setIcon(self.like_icon_empty)