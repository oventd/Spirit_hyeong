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
from constant import *

# 로깅 설정 (필요에 따라 파일 로깅 등 추가 가능)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class OpenManager:
    def __init__(self, context):
        self.context = context
        self.step = STEP_SHORT_DICT[context.step["name"]]
        dcc_config_path = "/home/rapa/NA_Spirit/open/config/open_step.json"
        self.dcc_opens_dict = load_classes_from_json(dcc_config_path)
        self.validate_input()

        self.open_class = self.dcc_opens_dict[self.step]

    def validate_input(self) -> None:
        """
        entity_type과 dcc가 올바른지 검증합니다.
        """
        if self.step not in self.dcc_opens_dict:
            raise ValueError(f"Invalid step: {self.step}. Please choose one of: {', '.join(self.dcc_opens_dict.keys())}.")
        
    def open_setup(self) -> None:
        task_id = self.context.task["id"]
        file_format = ".ma"
        print(f"Debug: open_setup() is passing task_id={task_id}, {file_format}")
        self.open_class.Open.setup(task_id=task_id, file_format=file_format)
        self.open_class.Open.reference(task_id=task_id, file_format=file_format)
    
    def validate(self):
        self.open_class.Publish.validate()
    
    def publish(self,session_path:str):
        self.open_class.Publish().publish(session_path,context=self.context)
        
