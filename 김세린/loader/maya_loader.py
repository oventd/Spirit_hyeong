import maya.mel as mel
import maya.cmds as cmds
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/load/loader')
from base_loader import Loader

class MayaLoader(Loader):
    def import_file(self, paths):
        """USD 파일을 마야에 임포트"""
        for path in paths: 
            if not os.path.exists(path):
                cmds.warning(f"USD file not found: {path}")
                continue
            
            try: 
                cmds.file(path, i=True, type="USD Import")
            except Exception as e:
                cmds.warning(f"Failed to import USD file {path}: {str(e)}")
                return False
        return True
    
    def reference_file(self, paths):
        """USD 파일을 마야에 레퍼런스로 추가"""
        try:
            cmds.file(new=True, force=True)
            for path in paths:
                if not os.path.exists(path):
                    cmds.warning(f"USD file not found: {path}")
                    continue
                cmds.file(path, reference=True)
        except Exception as e:
            cmds.warning(f"Failed to reference USD file {path}: {str(e)}")
        return True

# 로더 실행
loader = MayaLoader()
paths = ["/home/rapa/3D_usd/Kitchen_set/assets/IronBoard/IronBoard.usd"]

# 임포트 또는 레퍼런스 실행
result_import = loader.import_file(paths)
result_reference = loader.reference_file(paths)
