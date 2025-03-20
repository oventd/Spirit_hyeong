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

class AnimatingStep(StepOpenMaya):
    def __init__(self):
        super().__init__()
        print ("Animating initialized")

    class Open(StepOpenMaya.Open):

        @staticmethod
        def setup(task_id, file_format):
            print()
            # file_path = FlowUtils.get_upstream_file_for_currnet_file(task_id, file_format)

            # cmds.file(file_path, reference=True, namespace=":", returnNewNodes=True)

        @staticmethod 
        def reference(group_name="", task_id=None, file_format=".ma",use_namespace=False):
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
        def validate(rig_group_name = "rig"):
            """Rig 그룹이 존재하는지 확인"""
            if not MayaUtils.validate_hierarchy(rig_group_name):
                print(f"Validation failed: {rig_group_name} group does not exist.")
                return False

            # animCurveTL 노드 확인
            if not MayaUtils.validate_anim_curve():
                print("Validation failed: 'animCurveTL' node does not exist.")
                return False
            
            print("Validation passed: 모든 조건을 충족합니다.")
            return True

            # if not MayaUtils.validate_hierarchy(rig_group_name):
            #     print(f"Validation passed: {rig_group_name} group exists.")
            # else:
            #     print(f"Validation failed: {rig_group_name} group does not exist.")

            # # animCurveTL 노드 확인
            # if MayaUtils.validate_anim_curve():
            #     print("Validation passed: 'animCurveTL' node exists.")
            # else:
            #     print("Validation failed: 'animCurveTL' node does not exist.")
                
        # def publish(rig_group_name = "rig", export_path="/home/rapa/3D_usd/Overwatch_2_-_Ramattra"):
        #     if not cmds.objExists(rig_group_name):
        #         print(f"Error: Group '{rig_group_name}' does not exist.")
        #         return False
            
        #     cmds.select("rig")
        #     cmds.file(
        #         export_path,
        #         force=True,
        #         type="USD Export",
        #         exportSelected=True
        #         )
        #     print(f"{export_path}에서 USD export 완료")
        
        @staticmethod
        def publish(session_path: str,context ):
            """ 특정 그룹을 USD와 MB 파일로 export """
            StepOpenMaya.Publish.publish(session_path,context)
            

                            
            # sframe = int( cmds.playbackOptions( q=1, min=1 ) )
            # eframe = int( cmds.playbackOptions( q=1, max=1 ) )
            # handle = int(5)
            # step = float(0.25)

if __name__ == "__main__":
    animation = AnimatingStep()
    AnimatingStep.Open.setup()
    AnimatingStep.Open.reference_rig()
    AnimatingStep.Open.reference_asset()
    AnimatingStep.Open.reference_camera()
    AnimatingStep.Publish.validate()
    AnimatingStep.Publish.publish()