import maya.mel as mel
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/load/loadManager/dcc_work_file_creators')
from work_file_creator import WorkFileCreator

class MayaWorkFileCreator(WorkFileCreator):
    def create_work_file(self, library_file_path: str, save_path: str) -> None:
        print("Creating Maya work file...")
        # 예: Maya 전용 작업 파일 생성 로직 구현
 
        if not os.path.exists(library_file_path):
            print(f"USD file not found: {library_file_path}") # 함수화해서 재활용할 수
            return
        # 새로운 파일 생성
        cmds.file(new=True, force=True)
        cmds.file(library_file_path, i=True, type="USD Import")
     
         # import 된 새로운 파일 save as 

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        cmds.file(rename=save_path)
        cmds.file(save=True, type="mayaAscii")
        print(f"Work file created: {save_path}")
       
    
if __name__ == "__main__":
    work_file_creator = MayaWorkFileCreator()

    library_path = "/home/rapa/3D_usd/Kitchen_set/assets/OilBottle/OilBottle_v001.usd"
    save_path = ""

    work_file_creator.create_work_file(library_path, save_path)