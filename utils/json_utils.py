import json
import os

class JsonUtils:

    @staticmethod
    def read_json(file_path : str) -> dict:
        """
        지정된 JSON 파일을 읽어 딕셔너리로 반환합니다.
        파일이 없으면 빈 딕셔너리를 반환합니다.
        """
        if not os.path.exists(file_path):
            print(f"JSON file not found: {file_path}")
            return {}
        try:
            with open(file_path, "r") as file:
                if os.stat(file_path).st_size == 0:
                    return {}
                return json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"'{file_path}' contains invalid JSON data.")
        
    @staticmethod
    def write_json(file_path, data: dict) -> None:
        """
        주어진 데이터를 JSON 형식으로 파일에 저장합니다.
        :param data: 저장할 딕셔너리 데이터
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)