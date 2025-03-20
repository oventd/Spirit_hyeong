import maya.mel as mel
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/open/step')
from step_open_maya import StepOpenMaya
sys.path.append('/home/rapa/NA_Spirit/utils')
sys.path.append('/home/rapa/NA_Spirit/maya')
from maya_utils import MayaUtils
from sg_path_utils import SgPathUtils

class ModelingStep(StepOpenMaya):
    def __init__(self):
        super().__init__()
        print ("Opening modeling step")

    class Open(StepOpenMaya.Open):
        @staticmethod
        def setup(geo_group_name="geo", task_id=None, file_format=None):
            """ 모델링 작업을 위한 기본 그룹 생성 """
            MayaUtils.create_group(geo_group_name)
        
        def reference(group_name="rig", task_id=None, file_format=".ma", use_namespace=True):
            print("reference")

    class Publish(StepOpenMaya.Publish):
        @staticmethod
        def validate(geo_group_name="geo", child_list = ["Low", "High"]):
            """ 모델링 퍼블리시를 위한 기본 검증 """
            if not MayaUtils.validate_hierarchy(geo_group_name):
                print(f"Validation failed: '{geo_group_name}' does not exist.")
                return False
            
            # 하위 그룹 검증
            if not MayaUtils.validate_hierarchy(geo_group_name, child_list):
                print("Validation failed: Geo 그룹 하위에 Low와 High 그룹이 존재하지 않습니다.")
                return False

            print("Validation passed: 모든 조건을 충족합니다.")
            return True

        @staticmethod
        def publish(session_path: str ,context):
            """ 특정 그룹을 USD와 MB 파일로 export """
            StepOpenMaya.Publish.publish(session_path,context)


if __name__ == "__main__":
    modeling = ModelingStep()
    ModelingStep.Open.setup()
    ModelingStep.Publish.validate()
    # ModelingStep.Publish.publish()

    ModelingStep.Publish.publish(
        group_name="geo",
        session_path="/nas/spirit/spirit/assets/Prop/apple/MDL/work/maya/scene.v002.ma",
        step="modeling",
        category="modeling",
        group="geo"
    )