import os
import sys
sys.path.append('/home/rapa/NA_Spirit/utils/')
sys.path.append('/home/rapa/NA_Spirit/gui/')
from flow_utils import FlowUtils
from assetmanager import AssetService
from shotgun_api3 import Shotgun
from constant import SERVER_PATH, SCRIPT_NAME, API_KEY

VALID_ASSET_TYPES = {

    "Architecture": "Prop",
    "Vehicle" :    "Prop",

}


class SendAssetFlow:
    

    def __init__(self):
        self.sg = Shotgun(SERVER_PATH, SCRIPT_NAME, API_KEY)


    def get_asset_data(self, asset_list):
        """ID list를 매개변수로 받고 모든 필드를 리턴해주는 메서드"""
        asset_all_info = AssetService.get_assets_by_ids_all_return(asset_list)
        return asset_all_info
    
    def add_asset_project(self, project_id, code, discription, sg_asset_type):
        """ ShotGrid에서 동일한 code(이름)을 가진 Asset이 있는지 확인"""
        existing_asset = self.sg.find_one(
            "Asset",
            [["project", "is", {"type": "Project", "id": project_id}], ["code", "is", code]],
            ["id"]
        )

        #  만약 같은 이름이 있으면 추가하지 않음
        if existing_asset:
            print(f" 이미 존재하는 Asset입니다: {code} (ID: {existing_asset['id']})")
            return  # 중복되면 함수 종료

        #  중복이 없으면 새로 추가
        new_asset_data = {
            "project": {"type": "Project", "id": project_id},
            "code": code,
            "description": discription,
            "sg_asset_type": sg_asset_type,
            "sg_status_list": "fin"
        }

        new_asset = self.sg.create("Asset", new_asset_data)
        print(f" 새로운 Asset 생성 완료! ID: {new_asset['id']}")

    def redata_for_flow(self,asset_list):
        
        info_all = self.get_asset_data(asset_list)
        for info in info_all:
            code = info["name"]
            discription = info["description"]
            sg_asset_type = info["category"]
            print(sg_asset_type)
            sg_asset_type = VALID_ASSET_TYPES.get(sg_asset_type, "Prop")
            self.add_asset_project(127, code, discription, sg_asset_type)  #127은 나중에 project id와 교체해주세용

        
       

