from abc import *

class WorkFileCreator(ABC):
    @abstractmethod
    def create_work_file(self, library_file_path: str, file_path: str) -> None:
        """
        각 DCC에 맞는 작업 파일 생성 로직을 구현합니다.
        """
        pass