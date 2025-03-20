class Check:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # 올바른 싱글톤 생성
        return cls._instance  # 기존 인스턴스 반환

    def __init__(self):
        if hasattr(self, "_initialized"):  # 중복 초기화를 방지
            return
        self._dict = {}  # 내부에서 사용할 딕셔너리
        self._checked_items = []  # 내부에서 사용할 리스트
        self._initialized = True  # 초기화 완료 체크

    @property
    def dict(self):
        return self._dict  # self._dict 반환 (정상)

    @dict.setter
    def dict(self, value):
        self._dict = value  # self._dict 값 변경 (정상)

    @property
    def checked_items(self):
        return self._checked_items  #버그 수정! 올바르게 self._checked_items 반환

    @checked_items.setter
    def checked_items(self, value):
        self._checked_items = value  #  self._checked_items 값 변경 (정상)