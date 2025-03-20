import os
import sys
import shutil
import re

import logging

current_file_path = os.path.abspath(__file__)
spirit_dir = os.path.abspath(os.path.join(current_file_path, "../../../"))
utils_dir = os.path.abspath(os.path.join(spirit_dir, "utils"))
sys.path.append(utils_dir)

from class_loader import load_classes_from_json
from sg_path_utils import SgPathUtils

# 로깅 설정 (필요에 따라 파일 로깅 등 추가 가능)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class LoadManager:
    def __init__(self, root_path: str, dcc_config_path: str) -> None:
        self._root_path = root_path
        self.types = ["assets", "sequences"]
        self.default_file = "scene"
        dcc_config_path = "/home/rapa/NA_Spirit/load/manager/work_file_creators.json"
        self.dcc_creators = load_classes_from_json(dcc_config_path)

    @property
    def root_path(self) -> str:
        return self._root_path

    @root_path.setter
    def root_path(self, value: str) -> None:
        self._root_path = value

    def validate_inputs(self, entity_type: str, dcc: str) -> None:
        """
        entity_type과 dcc가 올바른지 검증합니다.
        """
        if entity_type not in self.types:
            raise ValueError(f"Invalid type: {entity_type}. Please choose 'assets' or 'sequences'.")
        if dcc not in self.dcc_creators:
            raise ValueError(f"Invalid dcc: {dcc}. Please choose one of: {', '.join(self.dcc_creators.keys())}.")

    def add_entity(self, library_file_path: str, entity_info: dict) -> None:
        """
        라이브러리 파일을 publish와 work 디렉토리에 복사하고 버전을 업데이트합니다.
        
        entity_info 딕셔너리는 다음 키를 포함해야 합니다.
          - entity_type: 'assets' 또는 'sequences'
          - category: 카테고리 (예: 'Prop')
          - entity: 에셋명 (예: 'Chair')
          - step: 작업 스텝 (예: 'MDL')
          - dcc: 'maya' 또는 'houdini'
          - work_ext: 작업 파일 확장자 (예: '.ma')
          - publish_ext: 퍼블리시 파일 확장자 (예: '.usd')
          - file_name: (선택) 기본 파일명, 미입력시 기본값 사용
        """
        entity_type = entity_info.get("entity_type")
        category = entity_info.get("category")
        entity = entity_info.get("entity")
        step = entity_info.get("step")
        dcc = entity_info.get("dcc")
        work_ext = entity_info.get("work_ext")
        publish_ext = entity_info.get("publish_ext")
        file_name = entity_info.get("file_name", self.default_file)
        
        self.validate_inputs(entity_type, dcc)
        
        publish_dir, work_dir = self.make_entity_dir(entity_type, category, entity, step, dcc)
        
        publish_version = self.search_version(publish_dir, file_name)
        publish_path = os.path.join(publish_dir, f"{file_name}.{publish_version}{publish_ext}")
        
        work_version = self.search_version(work_dir, file_name)
        work_path = os.path.join(work_dir, f"{file_name}.{work_version}{work_ext}")

        # 라이브러리 파일이 존재하는지 확인
        if not os.path.exists(library_file_path):
            raise FileNotFoundError(f"Library file not found: {library_file_path}")
        
        self.create_publish_file(library_file_path, publish_path)
        self.create_work_file(library_file_path, dcc, work_path)

    def search_version(self, directory: str, file_name: str) -> str:
        """
        주어진 디렉토리 내에서 파일명의 버전을 검색하여 다음 버전을 반환합니다.
        파일 이름 형식 예: scene.v001.ma
        """
        try:
            files = os.listdir(directory)
        except FileNotFoundError:
            files = []
        
        last_version = 0
        version_pattern = re.compile(rf"{re.escape(file_name)}\.v(\d{{3}})")
        for f in files:
            match = version_pattern.match(f)
            if match:
                try:
                    version_num = int(match.group(1))
                    last_version = max(last_version, version_num)
                except ValueError:
                    continue
        new_version = last_version + 1
        return f"v{new_version:03d}"

    def make_entity_dir(self, entity_type: str, category: str, entity: str, step: str, dcc: str) -> tuple[str, str]:
        """
        publish와 work 디렉토리를 생성합니다.
        """
        publish_dir = SgPathUtils.make_entity_file_path(self._root_path, entity_type, category, entity, step, version="publish", dcc="cache")
        os.makedirs(publish_dir, exist_ok=True)
        
        work_dir = SgPathUtils.make_entity_file_path(self._root_path, entity_type, category, entity, step, version="work", dcc=dcc)
        os.makedirs(work_dir, exist_ok=True)
        
        return publish_dir, work_dir

    def create_publish_file(self, library_file_path: str, publish_path: str) -> None:
        """
        라이브러리 파일을 publish 경로로 복사합니다.
        """
        directory = os.path.dirname(publish_path)
        os.makedirs(directory, exist_ok=True)
        try:
            shutil.copy(library_file_path, publish_path)
            logging.info(f"Published file created: {publish_path}")
        except Exception as e:
            logging.error(f"Error creating publish file: {e}")
            raise

    def create_work_file(self, library_file_path: str, dcc: str, file_path: str):
        """
        dcc에 맞는 work 파일 생성 크리에이터를 사용하여 작업 파일을 생성합니다.
        """
        creator = self.dcc_creators.get(dcc)
        if creator is None:
            raise ValueError(f"No work file creator defined for dcc '{dcc}'.")
        try:
            result = creator.create_work_file(library_file_path, file_path)
            if result is None:
                raise ValueError(f"Work file creator for dcc '{dcc}' returned None.")
            logging.info(f"Work file created: {file_path}")
            return result
        except Exception as e:
            logging.error(f"Error creating work file for {dcc}: {e}")
            raise

    def remove_entity(self, entity_info: dict) -> None:
        """
        해당 entity의 work 및 publish 파일을 삭제합니다.

        entity_info 딕셔너리는 다음 키를 포함해야 합니다.
          - entity_type: 'assets' 또는 'sequences'
          - category: 카테고리 (예: 'Prop')
          - entity: 에셋명 (예: 'Chair')
          - step: 작업 스텝 (예: 'MDL')
          - dcc: 'maya' 또는 'houdini'
        """
        entity_type = entity_info.get("entity_type")
        category = entity_info.get("category")
        entity = entity_info.get("entity")
        step = entity_info.get("step")
        dcc = entity_info.get("dcc")
        
        step_path = SgPathUtils.make_entity_file_path(self._root_path, entity_type, category, entity, step)
        asset_path = SgPathUtils.make_entity_file_path(self._root_path, entity_type, category, entity)

        if not os.path.exists(step_path):
            logging.warning(f"Entity not found: {entity_info}")
            return
        
        shutil.rmtree(step_path)
        if os.listdir(asset_path) == []:
            shutil.rmtree(asset_path)

        logging.info(f"Entity removed: {entity_info}")

if __name__ == "__main__":

    # 예: dcc_config.json 파일의 경로를 지정합니다.

    lm = LoadManager("/nas/sam/show/test", dcc_config_path)
    library_asset_path = "/home/rapa/Kitchen_set/assets/Chair/Chair.usd"
    entity_info = {
        "entity_type": "assets",
        "category": "Prop",
        "entity": "Chair",
        "step": "MDL",
        "dcc": "maya",
        "work_ext": ".ma",
        "publish_ext": ".usd"
    }
    lm.add_entity(library_asset_path, entity_info)
    lm.remove_entity(entity_info)
