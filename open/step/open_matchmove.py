import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/open/step')
from step_open_maya import StepOpenMaya
sys.path.append('/home/rapa/NA_Spirit/utils')
from maya_utils import MayaUtils

"""각 스텝에 맞는 match move 파일을 불러올 클래스입니다."""
class MatchMoveStep(StepOpenMaya):
    def __init__(self):
        super().__init__()
        print("Opening match move step")

    class Open(StepOpenMaya.Open):
        @staticmethod
        def setup(group_name="asset", camera_group_name="camera", camera_name="main_cam", task_id=None, file_format=None):
            MayaUtils.create_group(group_name)
            camera_name = MayaUtils.create_camera(group_name=camera_group_name, camera_name=camera_name)
        
        @staticmethod 
        def reference(group_name="rig", task_id=None, file_format=".ma", use_namespace=True):
            print("reference")
            
        
    class Publish(StepOpenMaya.Publish):
        @staticmethod
        def validate(group_name="asset", camera_group_name="camera", camera_name="main_cam"):
            """그룹 및 카메라 검증"""
            if not camera_name:
                camera_name = "main_cam"

            # 카메라 그룹 검증
            if not MayaUtils.validate_hierarchy(group_name=camera_group_name, child_list=[camera_name]):
                print(f"Validation failed: Camera '{camera_name}' does not exist in group '{camera_group_name}'.")
                return False

            # 환경 그룹 검증
            if not MayaUtils.validate_hierarchy(group_name):
                print(f"Validation failed: asset '{group_name}' does not exist.") 
                return False

            # # 카메라 그룹 검증
            # if MayaUtils.validate_hierarchy(group_name=camera_group_name, child_list=[camera_name]):
            #     print(f"Validation passed: Camera '{camera_name}' exists in group '{camera_group_name}'.")
            # else:
            #     print(f"Validation failed: Camera '{camera_name}' does not exist in group '{camera_group_name}'.")

            # # 환경 그룹 검증
            # if MayaUtils.validate_hierarchy(group_name):
            #     print(f"Validation passed: terrain '{group_name}' exists.")
            # else:
            #     print(f"Validation failed: terrain '{group_name}' does not exist.") 

        @staticmethod
        def publish(session_path: str ,context):
            """ 특정 그룹을 USD와 MB 파일로 export """
            StepOpenMaya.Publish.publish(session_path,context)

if __name__ == "__main__":
    matchmove = MatchMoveStep()
    MatchMoveStep.Open.setup()
    MatchMoveStep.Publish.validate()