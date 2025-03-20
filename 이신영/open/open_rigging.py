import maya.mel as mel
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/open/step')
from step_open_maya import StepOpenMaya
sys.path.append('/home/rapa/NA_Spirit/utils')
sys.path.append('/home/rapa/NA_Spirit/maya')
sys.path.append('/home/rapa/NA_Spirit/flow')
from maya_utils import MayaUtils
from sg_path_utils import SgPathUtils
from flow_utils import FlowUtils

"""각 스텝에 맞는 match move 파일을 불러올 클래스입니다."""
class RiggingStep(StepOpenMaya):
    def __init__(self):
        super().__init__()
        print("Opening rigging step")

    class Open(StepOpenMaya.Open):
        @staticmethod
        def setup(task_id=None, file_format=".ma"):
            group_name = "rig"
            group_name = MayaUtils.create_group(group_name)
            return group_name

        @staticmethod
        def reference(group_name="rig", task_id=None, file_format=".ma", use_namespace=True):
            file_path = FlowUtils.get_upstream_file_for_currnet_file(task_id, file_format)

            asset_name, _ = SgPathUtils.trim_entity_path(file_path)
            asset_name = os.path.basename(asset_name)
            step = SgPathUtils.get_step_from_path(file_path)
            name_space = f"{asset_name}_{step}"

            MayaUtils.reference_file(file_path, group_name, name_space, use_namespace=use_namespace)
            return group_name
   
    class Publish(StepOpenMaya.Publish):
        @staticmethod
        def validate(group_name="rig"):
            """그룹 및 카메라 검증"""

            # 환경 그룹 검증
            if not MayaUtils.validate_hierarchy(group_name):
                print(f"Validation failed: rig '{group_name}' does not exist.")
                return False
            
            print("Validation passed: 모든 조건을 충족합니다.")
            return True

        @staticmethod
        def publish(session_path ,context):
            print("No Work for Publishing rigging step")
            

if __name__ == "__main__":
    rigging = RiggingStep()
    RiggingStep.Open.setup()
    RiggingStep.Publish.validate()