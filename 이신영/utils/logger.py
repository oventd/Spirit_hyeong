import logging
import os
from datetime import datetime

def create_logger(task_name, log_directory=None):
    """
    주어진 작업 이름에 맞춰 로그 파일을 생성하고 로거를 반환하는 함수
    - task_name: 로그 파일의 접두어로 사용되는 작업 이름
    - log_directory: 로그 파일이 저장될 디렉토리 경로 (기본값: None, None이면 현재 작업 디렉토리에 생성)
    
    반환값:
    - logger: 로그를 기록할 로거 객체    
    """
    # 로그 파일 이름 생성
    if log_directory is None:
        log_filename = f"{task_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
    else:
        abs_path = os.path.abspath(log_directory)

        if os.path.isdir(abs_path):  # 디렉터리 경로인 경우
            log_dir = abs_path
            log_filename = f"{task_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        else:  # 파일 경로인 경우
            log_dir = os.path.dirname(abs_path)
            log_filename = os.path.basename(abs_path)

    os.makedirs(log_dir, exist_ok=True)  # 디렉터리가 존재하지 않으면 생성

    log_file_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger(task_name)

    if not logger.hasHandlers():  # 중복된 핸들러를 추가하지 않도록 확인
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger
