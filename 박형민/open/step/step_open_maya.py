from abc import ABC, abstractmethod
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/utils')
sys.path.append('/home/rapa/NA_Spirit/usd')
sys.path.append("/home/rapa/NA_Spirit/flow")
from json_utils import JsonUtils
from maya_utils import MayaUtils
from sg_path_utils import SgPathUtils
from usd_version_connector import UsdVersionConnector
from maya_reference_usd_exporter import MayaReferenceUsdExporter
from flow_utils import FlowUtils
from entity_usd_connector import EntityUsdConnector
from constant import *

class StepOpenMaya(ABC):
    def __init__(self):
        pass
    
    # Open
    class Open(ABC):
        @abstractmethod
        def setup(self):
            pass
        
        @abstractmethod
        def reference(self):
            pass

    # Publish   
    class Publish(ABC):

        def __init__(self):
            pass

        @abstractmethod
        def get_publish_settings():
            print("[DEBUG] get_publish_settings() called")
            if publish_settings is None:
                publish_settings = JsonUtils.read_json("/home/rapa/NA_Spirit/open/config/publish_settings.json")
            print(f"[DEBUG] get_publish_settings() returns: {publish_settings}")  # 디버깅용 출력
            return publish_settings  

        @abstractmethod     
        def get_caching_settings():
            if caching_settings is None:
                caching_settings = JsonUtils.read_json("/home/rapa/NA_Spirit/open/config/caching_settings.json")
            return caching_settings
        
        @abstractmethod
        def validate(self):
            pass
        
        @abstractmethod
        def publish(session_path: str,context):
            #step 가져오기
            step = SgPathUtils.get_step_from_path(session_path)
            
            # 퍼블리시 설정 및 렌더 설정 가져오기
            publish_settings = StepOpenMaya.Publish.get_publish_settings()
            
            if not publish_settings[step]:
                return
            
            # 캐시 설정 가져오기
            caching_settings = JsonUtils.read_json("/home/rapa/NA_Spirit/open/config/caching_settings.json")
            # 퍼블리쉬 경로 가져오기
            usd_export_path = StepOpenMaya.Publish.get_usd_export_path(session_path)
            usd_export_options = caching_settings.get("export_usd_static_mesh", {})

            # 애니메이팅 여부 확인
            if step == "MDL" or step == "RIG" or step == "MMV":
                animated = False

            else:
                animated = True
                frame_range = FlowUtils.get_cut_in_out(context.entity["id"])
                print("frame_range : ", frame_range)
            # publish
            published_usds = {}
            for item, options in publish_settings[step].items():
                if not options:
                    continue
                
                all = options.get("all", False)
                is_referenced = options.get("isReferenced",False)
                maya = options.get("maya", False)
                # 레퍼런스 오브젝트가 있을 경우. 레퍼런스 경로 처리
                if is_referenced is True:
                    
                    if all is True:
                        MayaReferenceUsdExporter(step, usd_export_path,item, export_animated = False,export_static = True,frame_range = frame_range).run()
                        root_usd_path = UsdVersionConnector.connect(usd_export_path)
                        published_usds[item] = [root_usd_path]
                    elif all is False:
                        MayaReferenceUsdExporter(step, usd_export_path, item, export_animated = True ,export_static = False,frame_range = frame_range).run()
                        root_usd_path = UsdVersionConnector.connect(usd_export_path)
                        published_usds[item] = [root_usd_path]
                
                # 레퍼런스 오브젝트가 없을 때는 전체 캐싱
                if is_referenced is False:
                    if all is True:
                        cmds.select(item)
                        if animated is True:
                            MayaUtils.file_export(usd_export_path,usd_export_options,frame_range=frame_range)
                        elif animated is False:
                            MayaUtils.file_export(usd_export_path,usd_export_options)
                        print(f"usd_export_path: {usd_export_path}")
                        root_usd_path = UsdVersionConnector.connect(usd_export_path)
                        print(f"root_usd_path: {root_usd_path}")
                        published_usds[item] = [root_usd_path]

            
            print(f"published_usds: {published_usds}")
            EntityUsdConnector(session_path).connect(published_usds)
            return 


        @staticmethod
        def export_cache(group_name, step, file_path=""):
            """ 퍼블리싱을 위한 공통 export 설정 로직 """

            # 퍼블리쉬 설정 가져오기
            publish_settings = StepOpenMaya.Publish.get_publish_settings()
            print(f"[DEBUG] export_setting() - publish_settings: {publish_settings}")  # 디버깅용 출력
            
            # Step이 존재하는지 확인
            step_settings = publish_settings.get(step) # "modeling"을 가져옴
            if step_settings is None:
                print(f"Error: Step '{step}' not found in publish settings.")
                return {}

            group_settings = step_settings.get(group_name) # "geo"를 가져옴
            if not group_settings:
                print(f"Warning: No settings found for group '{group_name}' in step '{step}'.")
                return False
            
            if not StepOpenMaya.Publish.validate(group_name):  
                print("Publish aborted: Validation failed.")
                return False

            
            for key, value in group_settings.items():
                if isinstance(value, bool):
                    value = {"all": value}

                if isinstance(value, dict) and value.get("all", False):
                    children = cmds.listRelatives(group_name, children=True) or []
                    print(f"all children {group_name}")
                else:
                    children = cmds.listRelatives(group_name, children=False) or []
                    print(f"specific children {group_name}")

            is_referenced = group_settings.get("isReferenced", False)

            if is_referenced:
                if not file_path:
                    print(f"file_path is not required")
                    return {}
                else:
                    MayaUtils.reference_file(file_path, group_name)
            return group_settings
 
        @staticmethod
        def render_setting(step, category, group):
            """ 렌더링 설정을 가져오는 메서드 """
            caching_settings = StepOpenMaya.Publish.get_caching_settings()

            # Step이 존재하는지 확인
            step_settings = caching_settings.get(step, {})
            if not step_settings:
                print(f"Warning: No render settings found for step '{step}'. Using defaults.")
                return {}

            return step_settings.get(category, {}).get(group, {}) or {}
        
        @staticmethod
        def get_maya_export_dir(session_path):
            """ 퍼블리쉬 경로 관련 메서드"""
            # 퍼블리쉬 경로 변경
            publish_path = SgPathUtils.get_publish_from_work(session_path) # work-> "publish" 

            # 파일 확장자명 변경

            maya_filename = SgPathUtils.get_maya_ext_from_mb(publish_path) # .mb  

            # 파일 최종 저장 경로
            maya_export_dir = SgPathUtils.get_maya_dcc_from_usd_dcc(maya_filename) # maya dir
           
            # # 디렉토리 존재 여부 확인 후 생성
            # for export_dir in [maya_export_dir, usd_export_dir]:
            #     if not os.path.exists(export_dir):
            #         os.makedirs(export_dir)
            return maya_export_dir
        @staticmethod
        def get_usd_export_path(session_path, suffix=False):
            """ 퍼블리쉬 경로 관련 메서드"""
            # 퍼블리쉬 경로 변경
            publish_path = SgPathUtils.get_publish_from_work(session_path) # work-> "publish" 

            # 파일 확장자명 변경
            usd_filename = SgPathUtils.get_usd_ext_from_maya_ext(publish_path) # .usd

            # 파일 최종 저장 경로
            usd_export_path = SgPathUtils.get_usd_dcc_from_usd_dcc(usd_filename) # usd dir                     

            return usd_export_path
            
            # # 디렉토리 존재 여부 확인 후 생성
            # for export_dir in [maya_export_dir, usd_export_dir]:
            #     if not os.path.exists(export_dir):
            #         os.makedirs(export_dir)
            # return maya_export_dir, usd_export_dir
        @staticmethod
        def maya_export(path):
            """ maya 파일 내보내는 파트 """
            # MB 파일 내보내기
            file, ext = os.path.splitext(path)
            if ext == ".mb":
                file_format = "mb"
            elif ext == ".ma":
                file_format = "ma"
            else:
                print(f"Unsupported file format: {ext}")
            if not MayaUtils.file_export(path, file_format=file_format):
                return False
            return True
        @staticmethod
        def get_animated_transform_nodes():
            """애니메이션 커브에 연결된 트랜스폼 노드를 가져옴"""
            anim_curves = cmds.ls(type="animCurve")
            animated_nodes = set()

            for curve in anim_curves:
                connected_nodes = cmds.listConnections(f"{curve}.output", source=False, destination=True)
                if connected_nodes:
                    animated_nodes.add(connected_nodes[0])

            return list(animated_nodes)
