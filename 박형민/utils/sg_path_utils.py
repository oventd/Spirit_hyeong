import os

class SgPathUtils:
    """Shotgun과 관련된 경로 유틸리티 클래스."""

    @staticmethod
    def make_entity_file_path(
        root_path: str,
        entity_type: str,
        category: str,
        entity: str,
        step: str = None,
        version: str = None,
        dcc: str = None,
        file: str = None
    ) -> str:
        """
        파일 경로를 생성합니다.

        :param  root_path (str): 루트 경로.
        :param  entity_type (str): 엔티티 유형 (예: 'assets' 또는 'sequences').
        :param  category (str): 카테고리 (예: 캐릭터, 소품 등).
        :param  entity (str): 엔티티 이름.
        :param  step (str, optional): 작업 단계 (예: 'Model', 'Rig', 'Anim'). Defaults to None.
        :param  version (str, optional): 버전 정보 (예: 'v001'). Defaults to None.
        :param  dcc (str, optional): 사용 DCC (예: 'maya', 'houdini'). Defaults to None.
        :param  file (str, optional): 파일 이름. Defaults to None.

        :return: str 생성된 파일 경로.
        """
        path_parts = [entity_type, category, entity]
        
        if step is not None:
            path_parts.append(step)
        if version is not None:
            path_parts.append(version)
        if dcc is not None:
            path_parts.append(dcc)
        if file is not None:
            path_parts.append(file)

        return os.path.join(root_path, *path_parts)

    @staticmethod
    def get_entity_type(path: str) -> str:
        """
        경로에서 entity_type을 판별합니다.

        :param  path:(str) 파일 또는 폴더 경로.

        :return: (str) 'sequences' 또는 'assets' 중 하나. 일치하는 것이 없으면 None.
        """
        if 'sequences' in path:
            return 'sequences'
        elif 'assets' in path:
            return 'assets'
        return None
    
    @staticmethod
    def trim_entity_path(entity_path):
        dirs = os.path.normpath(entity_path).split(os.sep)  # OS에 맞게 경로 정규화
        symbolic_index = -1

        # "assets" 또는 "sequences"가 포함된 첫 번째 위치 찾기
        for i, dir_name in enumerate(dirs):
            if dir_name in ("assets", "sequences"):
                symbolic_index = i
                break

        if symbolic_index == -1:
            raise ValueError(f"Invalid entity path (no 'assets' or 'sequences' found): {entity_path}")

        # "assets" 또는 "sequences" 이후 2개 더 포함 (총 3개 유지)
        symbolic_index_added = symbolic_index + 3

        if symbolic_index_added > len(dirs):  # num보다 커야 정상
            raise ValueError(f"Invalid entity path (too short): {entity_path}")

        trimmed_path = os.sep.join(dirs[:symbolic_index_added])
        trimmed_after = os.sep.join(dirs[symbolic_index_added:])
        return trimmed_path ,trimmed_after
    @staticmethod
    def get_publish_dir(entity_path, step):
        """
        entity_path에서 trim_entity_path로 경로를 간략화한 후,
        특정 작업(step)의 publish 디렉터리 경로를 반환합니다.

        예: '/project/show/assets/character/main', 'model'
            -> '/project/show/assets/character/main/model/publish'
        """
        trimmed_path = SgPathUtils.trim_entity_path(entity_path)
        return os.path.join(trimmed_path, step, "publish")

    @staticmethod
    def get_type(publish_file):
        """
        주어진 publish_file 경로에서 바로 상위 디렉터리의 이름을 반환합니다.

        예: '/project/show/assets/character/main/model/publish/usd/file.usd'
            -> 'usd'
        """
        SgPathUtils.trim_entity_path(publish_file)
        return os.path.basename(os.path.dirname(publish_file))
    @staticmethod
    def get_version(publish_file):
        return os.path.splitext(publish_file)[0].split(".")[1]
    

    @staticmethod
    def get_usd_publish_dir(entity_path, step):
        """
        특정 작업(step)의 USD publish 디렉터리 경로를 반환합니다.

        예: '/project/show/assets/character/main', 'model'
            -> '/project/show/assets/character/main/model/publish/usd'
        """
        publish_dir = SgPathUtils.get_publish_dir(entity_path=entity_path, step=step)
        return os.path.join(publish_dir, "usd")

    @staticmethod
    def get_maya_publish_dir(entity_path, step):
        """
        특정 작업(step)의 Maya publish 디렉터리 경로를 반환합니다.

        예: '/project/show/assets/character/main', 'model'
            -> '/project/show/assets/character/main/model/publish/maya'
        """
        publish_dir = SgPathUtils.get_publish_dir(entity_path=entity_path, step=step)
        return os.path.join(publish_dir, "maya")

    @staticmethod
    def get_publish_from_work(work_file):
        """
        work 경로를 publish 경로로 변환하여 반환합니다.
        """
        return work_file.replace("work", "publish")

    @staticmethod
    def get_work_from_publish(publish_file):
        """
        publish 경로를 work 경로로 변환하여 반환합니다.
        """
        return publish_file.replace("publish", "work")

    @staticmethod
    def get_maya_dcc_from_usd_dcc(path):
        """
        USD DCC 경로를 Maya DCC 경로로 변경합니다.
        """
        return path.replace('usd', 'maya')

    @staticmethod
    def get_usd_dcc_from_usd_dcc(path):
        """
        Maya DCC 경로를 USD DCC 경로로 변경합니다.
        """
        return path.replace('maya', 'usd')

    @staticmethod
    def get_maya_ext_from_usd_ext(usd_file):
        """
        USD 파일 확장자를 Maya 바이너리(.mb) 확장자로 변경합니다.
        """
        return usd_file.replace(".usd", ".mb")

    @staticmethod
    def get_usd_ext_from_maya_ext(maya_file):
        """
        Maya 파일 확장자(.ma, .mb)를 USD 확장자(.usd)로 변경합니다.
        지원되지 않는 확장자는 ValueError를 발생시킵니다.
        """
        if maya_file.endswith('.ma'):
            result = maya_file.replace(".ma", ".usd")
        elif maya_file.endswith('.mb'):
            result = maya_file.replace('.mb', '.usd')
        else:
            raise ValueError(f"Unsupported Maya file extension in {maya_file}")
        return result
    
    @staticmethod
    def get_maya_ext_from_mb(maya_file):
        """
        Maya 파일 확장자(.ma)를 (.mb)로 변경합니다.
        지원되지 않는 확장자는 ValueError를 발생시킵니다.
        """
        if maya_file.endswith('.ma'):
            result = maya_file.replace(".ma", ".mb")
        else:
            raise ValueError(f"Unsupported Maya file extension in {maya_file}")
        return result

    @staticmethod
    def get_step_from_path(path):
        entity_path, after_path = SgPathUtils.trim_entity_path(path)
        return after_path.split('/')[0]
    @staticmethod
    def get_category_from_path(path):
        entity_path, after_path = SgPathUtils.trim_entity_path(path)
        return entity_path.split('/')[-2]
    @staticmethod
    def set_step(publish_file, step):
        entity_path, after_path= SgPathUtils.trim_entity_path(publish_file)
        step_changed = after_path.split("/")
        step_changed[0] = step
        asset_name_and_version = step_changed[-1]
        asset_name_spilt = asset_name_and_version.split(".")
        asset_name_spilt[0] = asset_name_spilt[0][:-3]+step
        file_name = ".".join(asset_name_spilt)
        step_changed[-1] = file_name
        step_changed_path = "/".join(step_changed)
        result =  os.path.join(entity_path, step_changed_path)
        return result
    
if __name__ == "__main__":
    session_path = "/nas/spirit/spirit/assets/Prop/apple/MDL/work/maya/Mat_RIG.v002.ma"
    print(SgPathUtils.set_step(session_path,"MDL"))
