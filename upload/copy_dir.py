import shutil
import os

def copy_folder(source_folder: str, destination_folder: str):
    """
    특정 폴더를 대상 경로로 복사하는 메서드.
    
    :param source_folder: 원본 폴더 경로
    :param destination_folder: 복사할 대상 폴더 경로
    """
    # 대상 폴더가 없으면 생성
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    try:
        # 폴더 전체 복사
        shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)
        print(f"폴더 복사가 완료되었습니다: {source_folder} -> {destination_folder}")
    except Exception as e:
        print(f"폴더 복사 중 오류 발생: {e}")

# 사용 예시
source_path = "/nas/spirit/project/spirit/assets/Prop/wood"
destination_path = "/nas/spirit/DB/source/wood"

copy_folder(source_path, destination_path)
