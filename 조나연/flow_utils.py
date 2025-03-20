from shotgun_api3 import Shotgun
import os
import sys
sys.path.append('/home/rapa/NA_Spirit/utils')
from constant import SERVER_PATH, SCRIPT_NAME, API_KEY
import urllib.request
class FlowUtils:

    sg = Shotgun(SERVER_PATH, SCRIPT_NAME, API_KEY)
    
    @classmethod
    def upload_undistorted(cls,shot_id, width, height):    
    

        # 업데이트할 데이터
        data = {
            'sg_undistorted_width': f"{width}",
            'sg_undistorted_height': f"{height}"
        }

        # Shot 엔터티의 특정 필드 업데이트
        updated_shot = cls.sg.update('Shot', shot_id, data)

        # 결과 출력
        print(f"Updated Shot ID: {updated_shot['id']}, sg_undistorted_width: {updated_shot.get('sg_undistorted_width')}, sg_undistorted_height: {updated_shot.get('sg_undistorted_height')}")


    @classmethod
    def get_project_id_by_name(cls, project_name):  # 정상 작동
        """
        프로젝트 이름을 사용하여 프로젝트 ID를 가져오는 함수
        """
        project_data = cls.sg.find_one(
            "Project",
            [["name", "is", project_name]],
            ["id"]
        )

        if not project_data:
            print(f" Project '{project_name}' not found.")
            return None

        print(f"Project '{project_name}' has ID {project_data['id']}")
        return project_data["id"]
    
    
    @classmethod

    def get_all_shots_in_project(cls, project_id):
        """
        특정 프로젝트 내 모든 Shot의 ID와 Code를 가져오는 함수
        """
        try:
            shots = cls.sg.find(
                "Shot",  # Shot 엔티티 검색
                [["project", "is", {"type": "Project", "id": project_id}]],  # 특정 프로젝트 ID에 속한 Shot 찾기
                ["id", "code"]  # 가져올 필드: ID, 코드(이름)
            )

            if not shots:
                print(f" 프로젝트 ID에서 샷을 찾을 수가 없어요{project_id}.")
                return []

            print(f"Project ID : {project_id} 샷 갯수 : {len(shots)}")
            return shots 

        except Exception as e:
            print(f" Shot을 가져오는 중 오류 발생: {e}")
            return []
        

    
    @classmethod
    def get_assets_in_shot(cls, shot_id):
        """
        특정 Shot ID에 연결된 모든 Asset을 가져오는 함수.
        """
        if not isinstance(shot_id, int):
            try:
                shot_id = int(shot_id)  # Shot ID를 정수(int)로 변환
            except ValueError:
                print(f"샷 ID 오류에용'{shot_id}'")
                return None

        try:
            shot_data = cls.sg.find_one(
                "Shot",
                [["id", "is", shot_id]],  # 특정 Shot ID 필터
                ["id", "code", "assets"]  # Asset 정보 포함
            )

            if not shot_data or not shot_data.get("assets"):
                print(f"{shot_id}에서 에셋을 찾을 수 없어요.")
                return []

            asset_list = shot_data["assets"]
            print(f" {shot_id}에 {len(asset_list)}개의 에셋이 있어요.")
            return asset_list

        except Exception as e:
            print(f" {shot_id}를 가져오는 중, {e}: 오류가 생겼어요")
            return []




    @classmethod
    def find_asset_in_shot(cls, shot_id):

        used_asset_list =[]
        assets = cls.sg.find(
                "Asset",
                [["shots", "is",{"type":"Shot", "id":int(shot_id)}]],
                ["id","code","sg_asset_type"]
            )
        for asset in assets:

            used_asset_list.append(asset["code"])
        return used_asset_list



    @classmethod
    def get_cut_in_out(cls,SHOT_ID): 
        result = cls.sg.find(
                "Shot",
                [["id", "is",SHOT_ID]],
                ["sg_cut_in", "sg_cut_out"]
            )[0]
        return result["sg_cut_in"],result["sg_cut_out"]



    @classmethod
    def get_upstream_tasks(cls, task_id):
        """
        특정 Task의 Upstream Tasks(선행 작업)를 찾는 함수
        """
        if not isinstance(task_id, int):
            try:
                task_id = int(task_id)  # Task ID를 정수로 변환
            except ValueError:
                print(f" {task_id}라는 Task ID가 잘못되었습니다")
                return None

        try:
            task_data = cls.sg.find_one(
                "Task",
                [["id", "is", task_id]],  # 특정 Task ID 필터
                ["id", "content", "upstream_tasks"]  # Upstream Tasks 포함
            )

            if not task_data or not task_data.get("upstream_tasks"):
                print(f"{task_id}에 upstream tasks가 없어요")
                return []

            upstream_tasks = task_data["upstream_tasks"]
            print(f" {task_id}는 {len(upstream_tasks)}개의 upstream tasks를 가지고 있어요.")
            return upstream_tasks

        except Exception as e:
            print(f"Task ID에 대한 Upstream Tasks를 가져오는 중 오류 발생 {task_id}: {e}")
            return []
        
    @classmethod
    def get_upstream_published_files(cls, task_id, extensions=None):
        """
        특정 Task의 Upstream Tasks(선행 작업)의 퍼블리쉬된 파일 경로를 가져오는 함수.
        주어진 확장자(extensions)와 일치하는 파일만 반환한다.

        :param task_id: 기준이 되는 Task ID
        :param extensions: 필터링할 확장자의 리스트 (예: [".exr", ".abc"])
        :return: 필터링된 퍼블리쉬 파일 경로 리스트
        """
        if not isinstance(task_id, int):
            try:
                task_id = int(task_id)  # Task ID를 정수 변환
            except ValueError:
                print(f"{task_id}라는 Task ID가 잘못되었습니다")
                return None

        if extensions:
            # 확장자 리스트를 소문자로 통일
            extensions = {ext.lower() for ext in extensions}

        try:
            # 현재 Task의 Upstream Task 가져오기
            task_data = cls.sg.find_one(
                "Task",
                [["id", "is", task_id]],  # 특정 Task ID 필터
                ["id", "content", "upstream_tasks"]  # Upstream Tasks 포함
            )

            if not task_data or not task_data.get("upstream_tasks"):
                print(f"Task {task_id}에서 upstream tasks를 찾을 수 없습니다.")
                return []

            upstream_tasks = task_data["upstream_tasks"]
            upstream_task_ids = [t["id"] for t in upstream_tasks]

            print(f"Task {task_id}는 {len(upstream_tasks)}개의 upstream tasks를 가지고 있습니다.")

            # Upstream Task에서 퍼블리쉬된 파일 찾기
            upstream_files = cls.sg.find(
                "PublishedFile",
                [["task", "in", upstream_task_ids]],  # 업스트림 Task들의 퍼블리쉬 파일 검색
                ["id", "path_cache", "task"]
            )

            # 확장자 필터링 (extensions가 주어진 경우)
            if extensions:
                matching_files = [
                    file["path_cache"]
                    for file in upstream_files
                    if file.get("path_cache") and os.path.splitext(file["path_cache"])[-1].lower() in extensions
                ]
            else:
                matching_files = [file["path_cache"] for file in upstream_files if file.get("path_cache")]

            if not matching_files:
                print(f"Task {task_id}에서 주어진 확장자와 일치하는 업스트림 퍼블리쉬 파일이 없습니다.")
            else:
                print(f"Task {task_id}에서 찾은 업스트림 파일 경로들: {matching_files}")

            return matching_files

        except Exception as e:
            print(f"Task ID {task_id}의 업스트림 퍼블리쉬 파일을 가져오는 중 오류 발생: {e}")
            return []
            

    @classmethod
    def get_published_file_path(cls, task_id, file_format):
        """
        특정 Task의 PublishedFile 중 특정 확장자를 가진 파일의 경로를 반환하는 함수
        """
        try:
            published_files = cls.sg.find(
                "PublishedFile",
                [["task", "is", {"type": "Task", "id": task_id}]],
                ["id", "path"]
            )

            if not published_files:
                print(f"{task_id}에는 Published File이 없어요")
                return None

            for file in published_files:
                path_data = file.get("path", {})
                if not path_data:
                    print(f" {task_id}엔 path 데이터가 없어요")
                    continue

                local_path = path_data.get("local_path")
                if not local_path:
                    print(f" {task_id}엔 local path 데이터가 없어요")
                    continue

                _, file_extension = os.path.splitext(local_path)
                if file_extension == file_format:
                    return local_path

            print(f" {task_id}엔 {file_format} 포멧이 없어요")
            return None

        except Exception as e:
            print(f"{task_id}의 PublishedFile를 가져오면서 {e} 에러가 생겼어요")
            return None
        


    @classmethod
    def get_upstream_file_for_currnet_file(cls, current_task_id, file_format=".usd"):
        """
        현재 Task의 Upstream Task에서 특정 확장자의 파일 경로를 가져오는 함수
        """
        upstream_tasks = cls.get_upstream_tasks(current_task_id)

        if not upstream_tasks:
            print(f"{current_task_id}에서 upstream tasks를 찾을 수 없어요 ")
            return None

        for upstream_task in upstream_tasks:
            upstream_task_id = upstream_task["id"]
            file_path = cls.get_published_file_path(upstream_task_id, file_format)

            if file_path:
                print(f" upstream file를 찾았어요: {file_path}")
                return file_path

        print(f" 지금 task의 upstream 은 없습니다 지금 task : {current_task_id}")
        return None
    


    def update_published_file(cls,PUBLISHED_FILE_ID,published_file_data):

        """주어진 PUBLISHED_FILE_ID에 해당하는 
            PublishedFile 데이터를 갱신"""
        
        updated_published_file = cls.sg.update(
            "PublishedFile", 
            PUBLISHED_FILE_ID, published_file_data,  # 연결된 엔티티
            
        )

        return updated_published_file


    @classmethod
    def get_thumnail(cls,shot_id , save_path):
        asset = cls.sg.find_one("Asset", [["id", "is", shot_id]], ["image"])

        if asset and asset.get("image"):
            thumbnail_url=asset["image"]
        else:
            print("Thumbnail not found.")

        # 이미지 다운로드 및 저장
        urllib.request.urlretrieve(thumbnail_url, save_path)

        print(f"이미지가 {save_path}로 저장되었습니다!")

    @classmethod
    def get_asset_id(cls, project_id: int, asset_name: str) -> int:
        """
        프로젝트 ID와 에셋 이름을 사용하여 해당 에셋의 ID를 반환.

        :param project_id: 프로젝트 ID
        :param asset_name: 에셋 이름
        :return: 에셋 ID (없으면 -1 반환)
        """
        filters = [
            ["project", "is", {"type": "Project", "id": project_id}],
            ["code", "is", asset_name]
        ]
        fields = ["id"]
        
        result = cls.sg.find_one("Asset", filters, fields)

        if result:
            return result["id"]
        return -1  # 에셋을 찾지 못한 경우 -1 반환

if __name__ == "__main__":
    #아래 코드는 예시에용 업스트림 같은 파일 형식의 파일의 path를 가져오는 예시
    upstream_file_path=FlowUtils.get_upstream_file_for_currnet_file(6465,".ma")
    print(upstream_file_path)

    
    # a = FlowUtils.get_cut_in_out(1273)
    # print(a[0], a[1])


