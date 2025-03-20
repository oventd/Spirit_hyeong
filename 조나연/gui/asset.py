
class Asset:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # 올바른 싱글톤 생성
        return cls._instance  # 기존 인스턴스 반환

    def __init__(self):
        if hasattr(self, "_initialized"):  # 중복 초기화를 방지
            return
        self._current = {}
        self._initialized = True
    @property
    def current(self):
        return self._current  # _state 값을 반환

    @current.setter
    def current(self, value):
        self._current = value  # _state 값을 변경
