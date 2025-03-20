import os
import sys

utils_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../")) + "/utils"
sys.path.append(utils_dir)

from constant import *
from usd_utils import UsdUtils
from sg_path_utils import SgPathUtils


class EntityUsdConnector:
    def __init__(self, session_path: str):
        self.session_path = session_path
        self.entity_path, _ = SgPathUtils.trim_entity_path(session_path)
        self.entity_name = os.path.basename(self.entity_path)
        self.entity_usd_path = os.path.join(self.entity_path, self.entity_name+".usd")
    
        self.step = SHORT_STEP_DICT[SgPathUtils.get_step_from_path(session_path)]

        self.open_setup()

        self.entity_type = SgPathUtils.get_entity_type(self.entity_path)

        self.step_publish_data_dict = {
            MODELING: ["geo"],
            RIGGING: [],
            LOOKDEV: ["material"],
            MATCHMOVE: ["camera"],
            LAYOUT: ["asset"],
            ANIMATING: ["asset"],
            LIGHTING: ["light"],
        }
        # self.step_usd_dict = {}

        # Step을 문자열로 선언하여 객체를 동적으로 불러올 수 있도록 변경
        self.step_class_mapping = {
            MODELING: "Model",
            RIGGING: "Rig",
            LOOKDEV: "Lookdev",
            MATCHMOVE: "Matchmove",
            LAYOUT: "Layout",
            ANIMATING: "Animating",
            LIGHTING: "Light",
        }

    @staticmethod
    def get_arg_dict(geo=None, char=None, anim_cache=None, material=None, camera=None, light=None):
        return {
            "geo": geo,
            "asset": char,
            "material": material,
            "anim_cache": anim_cache,
            "camera": camera,
            "light": light,
        }

    def validate_args(self, provided_args):
        """ 단계별 필수 데이터를 검증하는 함수 """
        if self.step not in self.step_publish_data_dict:
            raise ValueError(f"Invalid step: {self.step}")

        required_keys = self.step_publish_data_dict.get(self.step, [])
        un_provided_keys = [arg for arg in required_keys if provided_args.get(arg) is None]

        if un_provided_keys:
            raise ValueError(f"Required keys not provided: {un_provided_keys}")

    def open_setup(self):
        """ 각 Step에 대한 USD 파일을 생성하는 함수 """
        if os.path.exists(self.entity_usd_path):
            self.entity_usd_stage = UsdUtils.get_stage(self.entity_usd_path)
            
            self.entity_root_prim = UsdUtils.get_prim(self.entity_usd_stage, "/Root")

        else:
            self.entity_usd_stage = UsdUtils.create_usd_file(self.entity_usd_path)
            
            self.entity_root_prim = UsdUtils.create_scope(self.entity_usd_stage, "/Root")
        
        # step_usd = os.path.join(self.entity_path, self.step, f"{self.entity_name}_{self.step}.usda")
        # UsdUtils.create_usd_file(step_usd)

        # self.step_usd_dict[self.step] = step_usd

    def connect(self, provided_args):
        """ 클래스 이름을 문자열로 저장하고, getattr()을 사용해 동적으로 로드 """
        if self.step == RIGGING:
            return
        
        self.validate_args( provided_args)

        class_name = self.step_class_mapping.get(self.step)
        if not class_name:
            raise ValueError(f"Unsupported step: {self.step}")

        # 올바르게 getattr을 호출해야 함 (self가 아니라 클래스에서 가져옴)
        step_class = getattr(EntityUsdConnector, class_name, None)
        if not step_class:
            raise ValueError(f"Step class {class_name} not found in {self.__class__.__name__}")

        # 동적으로 클래스 인스턴스 생성 후 실행
        processor = step_class(self)
        processor.connect(provided_args)

    # 내부 클래스들 정의
    class Model:
        def __init__(self, parent):
            self.parent = parent

        def connect(self, provided_args):
            geo_paths = provided_args["geo"]
            print(f"Processing Model step with geo: {geo_paths}")
            for geo_path in geo_paths:
                if geo_path:
                    entity_root_prim_path = "/Root"
                    geo_xform_path = os.path.join(entity_root_prim_path,"MDL")
                    geo_xform = UsdUtils.get_prim(self.parent.entity_usd_stage, geo_xform_path)
                    if not geo_xform:
                        geo_xform =UsdUtils.create_xform(self.parent.entity_usd_stage, geo_xform_path)
                    UsdUtils.add_reference(geo_xform, geo_path)


    class Lookdev:
        def __init__(self, parent):
            self.parent = parent
        def connect(self, provided_args):
            material_paths = provided_args["material"]
            print(f"Processing Lookdev step with material: {material_paths}")
            for material_path in material_paths:
                if material_path:
                    entity_root_prim_path = "/Root"
                    material_xform_path = os.path.join(entity_root_prim_path,"LDV")
                    mat_xform = UsdUtils.get_prim(self.parent.entity_usd_stage, material_xform_path)
                    if not mat_xform:
                        mat_xform =UsdUtils.create_xform(self.parent.entity_usd_stage, material_xform_path)
                    UsdUtils.add_reference(mat_xform, material_path)

    class Matchmove:
        def __init__(self, parent):
            self.parent = parent

        def connect(self, provided_args):
            camera_paths = provided_args["camera"]
            print(f"Processing Matchmove step with camera: {camera_paths}")
            for camera_path in camera_paths:
                if camera_path:
                    entity_root_prim_path = "/Root"
                    material_xform_path = os.path.join(entity_root_prim_path,"MMV")
                    mat_xform = UsdUtils.get_prim(self.parent.entity_usd_stage, material_xform_path)
                    if not mat_xform:
                        mat_xform =UsdUtils.create_xform(self.parent.entity_usd_stage, material_xform_path)
                    UsdUtils.add_reference(mat_xform, camera_path)

    class Layout:
        def __init__(self, parent):
            self.parent = parent

        def connect(self, provided_args):
            asset_paths = provided_args["asset"]
            camera_paths = provided_args["camera"]
            for asset_path in asset_paths:
                if asset_path:
                    entity_root_prim_path = "/Root"
                    geo_xform_path = os.path.join(entity_root_prim_path,"LAY")
                    geo_xform = UsdUtils.get_prim(self.parent.entity_usd_stage, geo_xform_path)
                    if not geo_xform:
                        geo_xform =UsdUtils.create_xform(self.parent.entity_usd_stage, geo_xform_path)
                    UsdUtils.add_reference(geo_xform, asset_path)
            
    class Animating:
        def __init__(self, parent):
            self.parent = parent

        def connect(self, provided_args):
            anim_cache_paths = provided_args["asset"]
            # camera_paths = provided_args["camera"]
            # print(f"Processing Animating step with anim_cache: {anim_cache_paths}, camera: {camera_paths}")
            # for camera_path in camera_paths:
            #     if camera_path:
            #         UsdUtils.add_sublayer(self.parent.entity_usd_stage, camera_path)
            for anim_cache_path in anim_cache_paths:
                if anim_cache_path:
                    entity_root_prim_path = "/Root"
                    geo_xform_path = os.path.join(entity_root_prim_path,"ANI")
                    geo_xform = UsdUtils.get_prim(self.parent.entity_usd_stage, geo_xform_path)
                    if not geo_xform:
                        geo_xform =UsdUtils.create_xform(self.parent.entity_usd_stage, geo_xform_path)
                    UsdUtils.add_reference(geo_xform, anim_cache_path)

    class Light:
        def __init__(self, parent):
            self.parent = parent

        def connect(self, provided_args):
            lights = provided_args["light"]
            print(f"Processing Lighting step with light: {lights}")
            for light in lights:
                if light:
                    UsdUtils.add_sublayer(self.parent.entity_usd_stage, light)


if __name__ == "__main__":
    session_path = "/nas/spirit/project/spirit/assets/Character/Mat/MDL/work/maya/scene.v004.ma"
    option = {'geo': ['/nas/spirit/project/spirit/assets/Character/Mat/MDL/publish/usd/scene.usd']}
    connector =  EntityUsdConnector(session_path)
    connector.connect(option)
