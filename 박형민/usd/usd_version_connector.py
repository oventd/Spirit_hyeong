import os
import sys

utils_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../")) + '/utils'
sys.path.append(utils_dir)

from constant import *
from usd_utils import UsdUtils
from sg_path_utils import SgPathUtils

class UsdVersionConnector:

    @staticmethod
    def get_root_path(publish_file_path):
        dir_path = os.path.dirname(publish_file_path)
        base_name = os.path.basename(publish_file_path)
        
        name, ext = os.path.splitext(base_name)
        file_name, version = name.split(".")  # 파일명과 버전 분리

        result = os.path.join(dir_path, file_name + ext)
        return result
    
    @staticmethod
    def connect(publish_file_path):
        root_path = UsdVersionConnector.get_root_path(publish_file_path)
        version = SgPathUtils.get_version(publish_file_path)

        if not os.path.exists(root_path):
            UsdUtils.create_usd_file(root_path)

        stage = UsdUtils.get_stage(root_path)
        if not stage:
            stage = UsdUtils.create_stage(root_path)  # ✅ USD 파일 생성
        
        root_prim_path = "/Root"
        root_scope = UsdUtils.get_prim(stage, root_prim_path)  # ✅ 수정
        if not root_scope:
            root_scope = UsdUtils.create_scope(stage, root_prim_path)

        UsdUtils.add_reference_to_variant_set(root_scope,"version", {version: publish_file_path}, set_default = True)
        
        return root_path

    
if __name__ == "__main__":
    publish_file_path = "/nas/spirit/spirit/assets/Prop/apple/MDL/publish/maya/scene.v001.usd"

    root_path = UsdVersionConnector.get_root_path(publish_file_path)
    print(root_path)

    print(UsdVersionConnector.connect(publish_file_path))
