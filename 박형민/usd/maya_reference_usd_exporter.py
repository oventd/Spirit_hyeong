# import maya.cmds as cmds
import os
import sys

# 프로젝트 경로 설정
UTILS_DIR = '/home/rapa/NA_Spirit/utils'
USD_DIR = '/home/rapa/NA_Spirit/usd/'
sys.path.append(UTILS_DIR)
sys.path.append(USD_DIR)

# 외부 모듈 임포트
from constant import *
from usd_utils import UsdUtils
from sg_path_utils import SgPathUtils
from usd_version_connector import UsdVersionConnector
from json_utils import JsonUtils
import maya.cmds as cmds

class MayaReferenceUsdExporter:
    """
    레퍼런스가 존재하는 maya씬내 데이터를 USD 캐싱하는 클래스
    """

    def __init__(self,step, usd_file_path, assets_node, export_animated=True, export_static=True, frame_range=None):
        self.step = step
        self.usd_file_path = usd_file_path
        self.stage = None
        self.assets_node = assets_node
        self.version  = SgPathUtils.get_version(self.usd_file_path)
        self.export_animated = export_animated
        self.export_static = export_static
        self.root_curve_name = "root"
        self.frame_range = frame_range
        self.export_setting_path = "/home/rapa/NA_Spirit/open/config/render_settings.json"

    def setup_usd(self):
        """
        USD 파일을 생성하거나 기존 파일을 불러옴
        """
        if os.path.exists(self.usd_file_path):
           os.remove(self.usd_file_path) 

        self.stage = UsdUtils.create_usd_file(self.usd_file_path)

    def print_references(self):
        """
        현재 씬의 모든 Reference 정보를 출력
        """
        references = cmds.ls(type="reference")
        if not references:
            print("No references found in the scene.")
            return

        for ref in references:
            ref_path = cmds.referenceQuery(ref, filename=True)
            is_loaded = cmds.referenceQuery(ref, isLoaded=True)
            associated_nodes = cmds.referenceQuery(ref, nodes=True) or []

            print(f"Reference Node: {ref}")
            print(f"  File Path: {ref_path}")
            print(f"  Loaded: {is_loaded}")
            print(f"  Associated Nodes: {associated_nodes}\n")

    def get_animated_transform_nodes(self):
        """
        애니메이션 커브에 연결된 트랜스폼 노드를 가져옴
        """
        anim_curves = cmds.ls(type="animCurve")
        animated_nodes = set()

        for curve in anim_curves:
            connected_nodes = cmds.listConnections(f"{curve}.output", source=False, destination=True)
            if connected_nodes:
                animated_nodes.add(connected_nodes[0])

        return list(animated_nodes)

    def get_parent_hierarchy(self, node):
        """
        주어진 노드의 부모 계층 구조를 반환
        """
        hierarchy = []
        current_node = node

        while True:
            parent = cmds.listRelatives(current_node, parent=True)
            if not parent:
                break
            hierarchy.append(parent[0])
            current_node = parent[0]

        return hierarchy
    
    def get_hierarchy_depth_to_references(root_group):
        """
        루트 그룹부터 레퍼런스까지의 계층 깊이를 반환
        """
        depth = 0
        current_group = root_group

        while True:
            children = cmds.listRelatives(current_group, children=True)
            if not children:
                break
            if cmds.referenceQuery(children[0], isNodeReferenced=True):
                depth += 1
                break

            depth += 1
            current_group = children[0]
        return depth
    

    def find_scene_animation_range(self):
        """
        씬의 애니메이션 프레임 범위를 찾음
        """
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
        return start_frame, end_frame

    def process_static_asset(self, category_scope_path, asset_name, usd_mod_root_file, root_transform):
        """
        애니메이팅이 없는 오브젝트를 레퍼런스 시키는 메서드
        """
        print(f"{asset_name} is a static object. Creating Xform and adding reference.")
        asset_xform = UsdUtils.create_xform(self.stage, f"{category_scope_path}/{asset_name}")
        print(f"Created Xform: {asset_name}")
        print(f"Adding reference to USD: {usd_mod_root_file}")
        
        UsdUtils.add_reference(asset_xform, usd_mod_root_file)
        print(f"Added reference: {usd_mod_root_file}")
        
        transform_translate = (root_transform['tx'], root_transform['ty'], root_transform['tz'])
        transform_rotate = (root_transform['rx'], root_transform['ry'], root_transform['rz'])
        transform_scale = (root_transform['sx'], root_transform['sy'], root_transform['sz'])

        UsdUtils.set_transform(asset_xform, translate=transform_translate, rotate=transform_rotate, scale=transform_scale)
        print("Transform applied.")

    @staticmethod
    def create_anim_asset_dir(usd_file_path, category, asset_name):
        """
        애니메이팅 캐시 usd를 저장할 dir를 만드는 매서드
        """
        usd_dir = os.path.dirname(usd_file_path)
        dir = os.path.join(usd_dir,category,asset_name)
        os.makedirs(dir, exist_ok=True)
        return dir
    
    def export_anim_asset_usd(self, asset_usd_dir, asset, asset_name, frame_range):
        """
        애니메이션 오브젝트를 USD로 내보내는 메서드
        """
        # 애니메이션 오브젝트 선택
        cmds.select(asset)
        export_path = os.path.join(asset_usd_dir,f"{asset_name}.{self.version}.usd")

        # USD Export 옵션
        export_options = JsonUtils.read_json(self.export_setting_path)["export_usd_animated_mesh"]

        export_options["startTime"] = self.frame_range[0]
        export_options["endTime"] = self.frame_range[1]
        # 딕셔너리를 문자열 옵션으로 변환
        export_options_str = ";".join(f"{key}={value}" for key, value in export_options.items())

        # USD export 실행
        cmds.file(export_path,
                  force=True,
                  options=export_options_str,
                  type="USD Export",
                  preserveReferences=True,
                  exportSelected=True)  
        return export_path

    def process_usd_animated_asset(self, category_scope_path, asset_name, anim_usd_path, mod_usd_path):
        """
        애니메이션 오브젝트를 처리하는 메서드
        """
        # 애님 캐시 usd를 레퍼런스 받을 xform 생성
        asset_xform = UsdUtils.create_xform(self.stage, f"{category_scope_path}/{asset_name}")
        print(f"Created Xform: {asset_name}")
        # 애님 캐시 usd를 레퍼런스
        print(f"Adding reference to USD: {asset_name}")
        UsdUtils.add_reference(asset_xform, anim_usd_path)
        print(f"Added reference: {anim_usd_path}")

        UsdUtils.create_variants_set(asset_xform, "state")
        UsdUtils.add_reference_to_variant_set(asset_xform, "state", {"modeling":mod_usd_path})
        UsdUtils.add_reference_to_variant_set(asset_xform, "state", {"anim_cache": anim_usd_path}, set_default=True)

    def process_assets(self):
        """
        Maya 씬 내의 대상 Assets를 USD캐싱
        """
        # export 할 그룹이 존재하는지 체크
        if not cmds.objExists(self.assets_node):
            raise ValueError("Assets node does not exist.")
        # 패스 생성
        category_nodes = cmds.listRelatives(self.assets_node, children=True) or []
        assets_scope = UsdUtils.create_scope(self.stage, f"/{self.assets_node}")
        assets_scope_path = UsdUtils.get_prim_path(assets_scope)
        # 애니메이팅 정보를 가져옴
        animated_nodes = self.get_animated_transform_nodes()
        anim_assets = [self.get_parent_hierarchy(node)[-3] for node in animated_nodes if len(self.get_parent_hierarchy(node)) >= 3]
        # usd 파일내 카테고리 hierarchy를 위해 scope를 생성
        for category in category_nodes:
            category_scope = UsdUtils.create_scope(self.stage, f"{assets_scope_path}/{category}")
            category_scope_path = UsdUtils.get_prim_path(category_scope)
            # 하위 에셋 그룹을 가져옴
            asset_nodes = cmds.listRelatives(category, children=True) or []
        # 에셋 처리
        for asset in asset_nodes:
            
            print(f"Processing animated asset: {asset}")
            # 에셋정보와 레퍼런스 정보를 가져옴
            asset_name = asset.split(":")[0]
            print(f"{asset}, {asset_name}")
            ref_node = cmds.referenceQuery(asset, referenceNode=True)
            ref_path = cmds.referenceQuery(ref_node, filename=True)

            # 현재 패스를 통하여 모델링 usd 파일 패스를 역산
            usd_path = ref_path.replace("maya", "usd")
            usd_mod_path = SgPathUtils.set_step(usd_path, MDL)
            print(usd_mod_path)
            usd_mod_root_file = os.path.splitext(usd_mod_path)[0].split(".")[0] + ".usd"
            
            # 만약 모델링 파일이 없을 경우 예외처리
            if not os.path.exists(usd_mod_root_file):
                raise ValueError(f"USD file not found: {usd_mod_root_file}")
            
            # root 커브의 transform 데이터를 저장
            root_transform_node = f"{asset.split(':')[0]}:{self.root_curve_name}"
            root_transform = {attr: cmds.getAttr(f"{root_transform_node}.{attr}") for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']}
            print(f"Root Transform: {root_transform}")
            
            if asset in anim_assets:
                # 애니메이팅이 있는 에셋은 캐싱후 레퍼런스
                if self.export_animated == False:
                    continue
                # 애니메이팅 캐시를 담을 dir 생성
                asset_usd_dir = self.create_anim_asset_dir(self.usd_file_path,category, asset_name)
                # 캐싱
                anim_usd_path = self.export_anim_asset_usd(asset_usd_dir, asset, asset_name, self.frame_range)
                
                print(f"Exporting: {self.frame_range} to {anim_usd_path}")
                # 퍼블리시된 캐시 버전을 root 파일에 연결
                anim_root_usd_path = UsdVersionConnector.connect(anim_usd_path)
                # 캐시 파일을 레퍼런스
                self.process_usd_animated_asset(category_scope_path, asset_name, anim_root_usd_path,usd_mod_root_file)
                
            else:
                # 애니메이팅이 없는 에셋은 리깅 커브의 값을 xform에 적용 후 레퍼런스
                if self.export_static == False:
                    continue
                self.process_static_asset(category_scope_path, asset_name, usd_mod_root_file, root_transform)

    def run(self):
        """USD 처리 실행"""
        self.setup_usd()
        self.process_assets()
        return self.usd_file_path

if __name__ == "__main__":
    # 실행 코드
    export_setting_path = "/home/rapa/NA_Spirit/open/config/render_settings.json"
    export_options = JsonUtils.read_json(export_setting_path)
    print(export_options)