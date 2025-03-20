import os
import sys
import importlib
from json_utils import JsonUtils

def load_classes_from_json(json_file_path: str) -> dict:
    """
    JSON 파일을 읽고, 동적으로 클래스를 로드하여 인스턴스를 생성하는 함수입니다.

    JSON 파일의 각 항목에는 다음과 같은 정보가 포함되어야 합니다:
        {
            "key_name": {
                "module": "module_name",  # 모듈명
                "class": "ClassName",    # 클래스명
                "path": "relative_or_absolute_path_to_module"  # (선택사항) 모듈의 경로
            }
        }

    - JSON 파일에서 모듈과 클래스를 가져와 인스턴스를 생성하고, 딕셔너리 형태로 반환합니다.
    - 모듈 경로가 절대경로가 아니라면 현재 스크립트의 디렉토리를 기준으로 상대경로로 해석합니다.
    - 필요한 경우 sys.path에 모듈 디렉토리를 추가하여 동적 임포트가 가능하도록 합니다.

    :param json_file_path: JSON 파일 경로 (절대경로 또는 상대경로)
    :return: { "key_name": class_instance, ... } 형태의 딕셔너리 (클래스 인스턴스 매핑)
    """

    # JSON 파일 존재 여부 확인
    if not os.path.exists(json_file_path):
        print(f"JSON file not found: {json_file_path}")
        return {}

    # JSON 파일을 읽어 딕셔너리로 변환
    data_dict = JsonUtils.read_json(json_file_path)
    
    # 생성된 클래스 인스턴스를 저장할 딕셔너리
    loaded_classes = {}

    # 현재 실행 중인 파일이 위치한 디렉토리
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for key, info in data_dict.items():
        # JSON에서 모듈명과 클래스명 추출
        module_name = info.get("module")  # 모듈명
        class_name = info.get("class")    # 클래스명
        module_file_path = info.get("path")  # (선택사항) 모듈 경로

        # 모듈 또는 클래스 정보가 없는 경우 스킵
        if not module_name or not class_name:
            print(f"Skipping '{key}' due to missing module or class information.")
            continue

        # 모듈 경로가 지정된 경우, 절대경로인지 확인
        if module_file_path:
            if not os.path.isabs(module_file_path):
                # 절대경로가 아니라면 현재 스크립트 기준으로 상대 경로 변환
                module_file_path = os.path.join(base_dir, module_file_path)
            # 파일 경로라면 해당 파일이 위치한 디렉토리를 모듈 디렉토리로 사용
            module_directory = os.path.dirname(module_file_path)
        else:
            module_directory = None

        # 모듈 디렉토리를 sys.path에 추가하여 임포트 가능하게 함
        if module_directory and module_directory not in sys.path:
            sys.path.append(module_directory)
            print(f"Added to sys.path: {module_directory}")


        try:
            # 모듈 임포트
            module = importlib.import_module(module_name)
            # 모듈에서 클래스 가져오기
            class_ref = getattr(module, class_name)
            # 클래스 인스턴스 생성
            loaded_classes[key] = class_ref()
            print(f"Loaded '{key}' class from module '{module_name}'.")
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Error loading '{key}' class: {e}")

    return loaded_classes
