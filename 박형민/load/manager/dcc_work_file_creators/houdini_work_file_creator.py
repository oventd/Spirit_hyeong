from work_file_creator import WorkFileCreator

class HoudiniWorkFileCreator(WorkFileCreator):
    def create_work_file(self, library_file_path: str, file_path: str) -> None:
        print("Creating Houdini work file...")
        # Houdini 전용 작업 파일 생성 로직 구현
        pass