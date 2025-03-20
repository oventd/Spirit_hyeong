from db_client import MongoDBClient
from bson import ObjectId
from datetime import datetime
import pymongo
import os
import sys
utils_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../../"))+'/utils'
sys.path.append(utils_dir)
from logger import *
from constant import * 

class DbCrud:
    def __init__(self, logger_name=LOGGER_NAME, log_path=None, collection=None):
        """
        DbCrud 클래스의 생성자.
        - MongoDBClient을 사용하여 데이터베이스와 컬렉션을 설정합니다.
        - 로깅을 위한 기본 설정을 초기화합니다.
        
        이 클래스는 MongoDB와의 연결,로그를 설정합니다.
        :param logger_name: 로거 이름
        :param log_path: 로그 파일 경로
        :param collection: 사용할 MongoDB 컬렉션
        """
        self.db = MongoDBClient.get_db()

        if collection:
            self.collection = collection
        else:
            self.collection = self.db[USER_COLLECTION]

        log_path = log_path or DB_LOGGER_DIR
        self.logger = create_logger(logger_name, log_path)

    # Create (데이터 생성 또는 업데이트)
    def upsert_data(self, filter_conditions, update_fields=None):
        """
        에셋이 없으면 생성하고, 있으면 업데이트하는 메서드.
        :param filter_conditions: 찾을 조건 (dict)
        :param update_fields: 삽입 또는 업데이트할 필드 (dict)
        :return: 업데이트 또는 삽입된 문서의 ID
        """
        if not update_fields:
            raise ValueError("업데이트할 필드가 제공되지 않았습니다.")
        
        existing_document = self.collection.find_one(filter_conditions)
        
        if existing_document:
            # 기존 데이터가 있으면 업데이트만 수행
            update_data = {"$set": {"updated_at": datetime.utcnow()}}  # 변경 시간 갱신

            if update_fields:
                update_fields_copy = update_fields.copy()

                for key, value in update_fields_copy.items():
                    if existing_document.get(key) == value:
                        print(f"'{key}' 필드 값이 동일하므로 업데이트하지 않습니다.")
                        update_fields.pop(key)  # 동일한 값은 업데이트 리스트에서 제거
                # 업데이트 필드 적용
                update_data["$set"].update(update_fields)

            # 데이터가 존재하면 업데이트
            result = self.collection.update_one(filter_conditions, update_data, upsert=False)
            print(f"기존 자산 업데이트 완료")

        # 데이터가 없으면 새로 생성
        else:
            new_data = {
                **filter_conditions,  # filter_conditions에 있는 데이터 추가
                "created_at": datetime.utcnow(),  # 최초 생성 시간 추가
                "updated_at": datetime.utcnow()   # 변경 시간 추가
            }
            new_data.update(update_fields)

            # 새로 삽입
            result = self.collection.update_one(filter_conditions, {"$set": new_data}, upsert=True)
            print(f"새로운 자산 생성: {result.upserted_id}")

        return result
    
    # Read(조회 쿼리 파이프라인 생성)
    def construct_query_pipeline(self, filter_conditions=None, sort_by=None, sort_order=None,
                                limit=0, skip=0, fields=None, user_query =None):
        """
        MongoDB 쿼리 파이프라인을 생성하는 공통 함수입니다.
        주어진 조건을 바탕으로 쿼리 파이프라인을 동적으로 생성하여,
        다양한 필터링, 정렬, 페이징 등을 처리할 수 있습니다.

        :param filter_conditions: 문서 필터링 조건을 지정하는 딕셔너리
        :param sort_by: 정렬 기준이 되는 필드명
        :param sort_order: 정렬 순서
        :param limit: 결과의 최대 개수를 제한
        :param skip: 결과에서 건너뛸 개수
        :param fields: 반환할 필드를 지정하는 리스트
        :param user_query: 텍스트 검색을 위한 검색어
        
        :return: MongoDB 쿼리 파이프라인을 구성한 리스트
        """
        query_filter = {} # 필터 조건 저장 딕셔너리

        default_sort_orders = {
            CREATED_AT: (CREATED_AT, pymongo.DESCENDING),
            UPDATED_AT: (UPDATED_AT, pymongo.ASCENDING),
            DOWNLOADS: (DOWNLOADS, pymongo.DESCENDING),
        }
        
        pipeline = [] # 쿼리 파이프라인
        if limit:
            pipeline.append({"$limit": limit})
        if skip:
            pipeline.append({"$skip": skip})

        if filter_conditions: # 필터링 설정
            for key, value in filter_conditions.items():
                if isinstance(value, list):
                    query_filter[key] = {"$in": value}
                else:
                    query_filter[key] = value

        projection = {} # 반환 필드 설정         
        if fields:
            for field in fields:
                if field.startswith("$"):
                    raise ValueError(f"에러 지원하지 않는 필드명: {field}")
                projection[field] = 1
        if projection:
            pipeline.append({"$project": projection})       

        pipeline.insert(0,{"$match": query_filter})
        
        # 검색 기능 sort_by
        sort_conditions = {}        
        if user_query is not None:
            query_filter["$text"] = {"$search": user_query}  # 텍스트 검색 조건
            projection["score"] = {"$meta": "textScore"}  # 검색 점수
            sort_conditions = {"textScore": -1}

            if sort_by in default_sort_orders:
                sort_by, sort_order = default_sort_orders.get(sort_by, (sort_by, pymongo.ASCENDING))
                sort_conditions[sort_by] = sort_order
            pipeline.append({"$sort": sort_conditions})

        # 이외 기능의 sort_by
        elif sort_by:
            sort_by, sort_order = default_sort_orders.get(sort_by, (sort_by, pymongo.ASCENDING))
            pipeline.append({"$sort": {sort_by: sort_order}})
            print(f"기본 정렬 기준 적용: {sort_by}, {sort_order}")

        # sort_by가 제공되지 않았을 때 기본값을 설정
        if not sort_by:
            sort_by = CREATED_AT
            sort_order = pymongo.DESCENDING
            print(f"기본 정렬 기준 적용: {sort_by}, {sort_order}")

        # default_sort_orders에서 추가 정렬 조건 설정
        if sort_by in default_sort_orders:
            sort_by, sort_order = default_sort_orders.get(sort_by, (sort_by, pymongo.ASCENDING))

        print(f"최종 정렬 기준 적용: {sort_by}, {sort_order}")



        self.logger.debug(f"Generated Query Pipeline: {pipeline}")
        return pipeline

    # Read(데이터 조회)
    def find(self, filter_conditions=None, sort_by=None, sort_order=None, limit=0, skip=0, fields=None):
        """
        데이터를 조회하고, 필요한 경우 정렬 및 필터링을 수행합니다.
        :param filter_conditions: 필터 조건
        :param sort_by: 정렬 기준 필드
        :param sort_order: 정렬 순서
        :param limit: 조회할 데이터 개수
        :param skip: 건너뛸 데이터 개수
        :param fields: 반환할 필드 목록
        :return: 조회된 문서 리스트
        """        
        query_filter = {} # 필터 조건 딕셔너리

        # 필터 조건이 리스트 형식인 경우
        if isinstance(filter_conditions, list):
            object_ids = []
            for value in filter_conditions:
                if isinstance(value, str):
                    object_ids.append(ObjectId(value))  # 문자열이면 ObjectId로 변환
                elif isinstance(value, ObjectId):
                    object_ids.append(value)
            query_filter["_id"] = {"$in": object_ids}

        # 필터 조건이 딕셔너리인 경우
        elif isinstance(filter_conditions, dict):
            query_filter.update(filter_conditions)  

        pipeline = self.construct_query_pipeline(query_filter, sort_by, sort_order, limit, skip, fields)
        result = list(self.collection.aggregate(pipeline))

        self.logger.info(f"Query executed with filter: {filter_conditions} | Found: {len(result)} documents")
        return result
    
    def find_one(self, object_id, fields=None):
        """
        자산의 고유 ID를 기준으로 자산을 조회하여 상세 정보를 반환하는 함수입니다.
        자산 ID로 해당 자산을 찾고, 선택적으로 필요한 필드만 반환합니다.
        :param object_id: 자산의 고유 ID
        :param fields: 반환할 필드를 지정하는 리스트
        :return: 자산의 상세 정보
        """
        projection = None 
        # 필드가 주어지면 해당 필드 반환
        if fields:
            projection = {}
            for field in fields:
                projection[field] = 1
        # 자산 ID로 쿼리
        query_filter = {OBJECT_ID: ObjectId(object_id)}  

        details = self.collection.find_one(query_filter, projection)

        self.logger.info(f"Retrieved document ID: {object_id} | Document Details: {details}")
        return details
    
    def search(self, filter_conditions=None, limit=0, skip=0, fields=None, 
               sort_by=None, sort_order=None, user_query = None):
        """
        검색어를 기반으로 데이터를 검색하고, 검색 점수를 기준으로 정렬하는 함수입니다.
        주어진 조건에 맞는 데이터를 검색하고, 결과를 반환합니다.

        :param user_query: 사용자 검색어
        :param filter_conditions: 검색 결과에 추가적인 필터링을 적용할 조건
        :param limit: 조회할 데이터 개수 제한
        :param skip: 건너뛸 데이터 개수
        :param fields: 반환할 필드를 지정하는 리스트 (기본값은 `SEARCH_FIELDS` 상수)
        :param sort_by: 정렬 기준이 되는 필드명
        :param sort_order: 정렬 순서
        :return:
        """
        # 필드 기본 값
        if fields == None:
            fields = SEARCH_FIELDS

        pipeline = self.construct_query_pipeline(filter_conditions, sort_by, sort_order, limit, skip, fields, user_query=user_query)
        result = list(self.collection.aggregate(pipeline))

        self.logger.info(f"Search executed with query: {user_query} | Found: {len(result)} documents")
        return result

    # Update(다운로드 수 증가)
    def increment_count(self, object_id, field):
        """
        자산의 다운로드 수를 증가시킵니다.
        :param object_id: 다운로드 수를 증가시킬 자산의 ID
        :return: 다운로드 수 증가 여부 (True/False)
        """
        result = self.collection.update_one(
            {OBJECT_ID: ObjectId(object_id)},
            {"$inc": {field: 1}},
            upsert=False
        )

        self.logger.info(f"Incremented download count for document ID: {object_id}")
        return result.modified_count > 0  

    # Delete(데이터 삭제)
    def delete_one(self, object_id):
        """
        자산을 삭제합니다.
        :param object_id: 삭제할 자산의 ID
        :return: 삭제 성공 여부 (True/False)
        """
        result = self.collection.delete_one({OBJECT_ID: ObjectId(object_id)})  # 자산 ID를 기준으로 삭제
        
        self.logger.info(f"Deleted document ID: {object_id} | Acknowledged: {result.acknowledged}")
        return result.acknowledged


# Spirit에서 구현되는 클래스(자식 클래스)
class AssetDb(DbCrud):
    def __init__(self, log_path=None):
        super().__init__(logger_name=ASSET_LOGGER_NAME, log_path=log_path, collection=self.db[USER_COLLECTION])
        self.setup_indexes()

    def setup_indexes(self):
            """자산 컬렉션에 대한 인덱스 설정"""
            # self.asset_collection.create_index([(FILE_FORMAT, pymongo.ASCENDING)])
            # self.asset_collection.create_index([(UPDATED_AT, pymongo.DESCENDING)])
            # self.asset_collection.create_index([(UPDATED_AT, pymongo.ASCENDING)])
            # self.asset_collection.create_index([(DOWNLOADS, pymongo.DESCENDING)])
            # self.asset_collection.create_index(
            #     [(NAME, "text"), (DESCRIPTION, "text")],
            #     weights={NAME: 10, DESCRIPTION: 1}  # 'name' 필드에 10, 'description' 필드에 1의 가중치 부여
            # )
            # self.asset_collection.create_index(
            #     [("project_name", pymongo.ASCENDING), ("name", pymongo.ASCENDING)], unique=True)
            # self.logger.info("Indexes set up for AssetDb")

    # Create (에셋 생성 및 업데이트)
    def upsert_asset(self, asset_data):
        """
        자산 데이터를 업데이트하거나 새로 추가합니다.
        :param asset_data: 자산 데이터 (딕셔너리 형태)
        """
        # upsert_data(asset_data)
        project_name = asset_data.get("project_name")
        asset_name = asset_data.get("name")

        if not project_name or not asset_name:
            raise ValueError("필수 필드 'project_name'과 'name'이 제공되지 않았습니다~~!")
        
        filter_conditions = {"project_name": project_name, "name": asset_name}

        # 업데이트할 필드 설정
        update_fields = {}
        for key, value in asset_data.items():
            if key not in ["project_name", "name"]:
                update_fields[key] = value

        result = super().upsert_data(filter_conditions=filter_conditions, update_fields=update_fields)
        return result

if __name__ == "__main__":
    db = DbCrud()
    