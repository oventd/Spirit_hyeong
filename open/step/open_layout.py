import maya.mel as mel
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/open/step')
from step_open_maya import StepOpenMaya
sys.path.append('/home/rapa/NA_Spirit/utils')
from maya_utils import MayaUtils
from sg_path_utils import SgPathUtils
from flow_utils import FlowUtils

class LayoutStep(StepOpenMaya):
    def __init__(self):
        super().__init__()
        print ("layout initialized")

    class Open(StepOpenMaya.Open):
        @staticmethod
        def setup(task_id, file_format):
            print()
            # file_path = FlowUtils.get_upstream_file_for_currnet_file(task_id, file_format)

            # cmds.file(file_path, reference=True, namespace=":", returnNewNodes=True)
            
        @staticmethod 
        def reference(group_name = "asset", task_id=None, file_format=".ma", use_namespace=False):
            """
            주어진 그룹을 생성하고, 해당 그룹에 필요한 파일을 참조하는 함수.
            """
            file_path = FlowUtils.get_upstream_file_for_currnet_file(task_id, file_format)

            if not file_path or not os.path.exists(file_path):
                cmds.warning(f"[WARNING] No valid upstream file found for {group_name} ({file_path})")
                return None

            asset_name, _ = SgPathUtils.trim_entity_path(file_path)
            asset_name = os.path.basename(asset_name)
            step = SgPathUtils.get_step_from_path(file_path)
            name_space = f"{asset_name}_{step}"

            MayaUtils.reference_file(file_path, group_name, name_space, use_namespace=use_namespace)
            return group_name

    class Publish(StepOpenMaya.Publish):
        @staticmethod
        def validate(rig_group_name = "rig", asset_group_name="asset", camera_group_name="camera"):
            
            exception_group = {"rig"} # 검증 예외처리 할 객체

            # rig 그룹이 존재하는지 체크
            if not MayaUtils.validate_hierarchy(rig_group_name, exception_group=exception_group):
                print(f"Validation failed: Rig group '{rig_group_name}' does not exist.")  
                return False

            # asset 그룹이 존재하는지 체크
            if not MayaUtils.validate_hierarchy(asset_group_name):
                print(f"Validation failed: asset '{asset_group_name}' does not exist.")  
                return False

            # camera 그룹이 존재하는지 체크
            if not MayaUtils.validate_hierarchy(camera_group_name):
                print(f"Validation failed: Camera group '{camera_group_name}' does not exist.")  
                return False  
        
        @staticmethod
        def publish(session_path: str,context ):
            """ 특정 그룹을 USD와 MB 파일로 export """
            StepOpenMaya.Publish.publish(session_path,context)

            
if __name__ == "__main__":
    layout = LayoutStep()
    LayoutStep.Open.setup()
    LayoutStep.Publish.validate()

