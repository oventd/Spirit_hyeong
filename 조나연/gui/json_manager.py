import json
import os

class DictManager:
    file_path = '/nas/spirit/gui/json/like_asset_data.json'  # 클래스 변수로 파일 경로 설정

    @classmethod
    def save_dict_to_json(cls, data_dict):
        """
        주어진 dict를 JSON 파일에 저장하는 클래스 메서드.
        
        :param data_dict: 저장할 dict 데이터
        """
        if not isinstance(data_dict, list):
            print("잘못된 형식이에요 오브젝트 id가 들어있는 list형식만 가능합니다")  # 리스트가 아니면 None 반환 
        try:
            with open(cls.file_path, 'w') as json_file:
                json.dump(data_dict, json_file, indent=4)  # 데이터를 JSON 형식으로 저장
            print(f"liked_asset 저장 완료 : {cls.file_path}")
        except Exception as e:
            print(f"liked_asset 저장 실패 : {e}")
    
    @classmethod
    def load_dict_from_json(cls):
        """
        JSON 파일에서 dict를 불러오는 클래스 메서드.
        만약 파일이 없다면 빈 dict를 생성하여 반환
        
        :return: 불러온 dict 데이터 또는 빈 dict
        """
        try:
            if not os.path.exists(cls.file_path):  # 파일이 없으면 빈 dict를 생성
                print(f"{cls.file_path} 없네요. json 생성 할게요!")
                return {}

            with open(cls.file_path, 'r') as json_file:
                data_dict = json.load(json_file)  # JSON 파일에서 데이터를 불러옴
            return data_dict
        except Exception as e:
            print(f"liked_asset 로드 실패: {e}")
            return {}

            

