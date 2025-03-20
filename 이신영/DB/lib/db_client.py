import pymongo
from pymongo.errors import ConnectionFailure
import threading
import sys
import os
utils_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../../"))+'/utils'
sys.path.append(utils_dir)
from constant import MONGODB_ADRESS, DATA_BASE

class MongoDBClient:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        """
        MongoDB 클라이언트를 반환
        이미 클라이언트가 존재하면 재사용
        """
        if cls._client is None:
            try:
                cls._client = pymongo.MongoClient(
                    MONGODB_ADRESS, maxPoolSize=50, minPoolSize=5
                )
                print("MongoDB가 성공적으로 접속 되었어요.")
            except ConnectionFailure as e:
                print(f"MongoDB 연결이 실패했어요: {e}")
                raise
        return cls._client

    @classmethod
    def get_db(cls):
        """데이터베이스 인스턴스를 반환"""
        if cls._db is None:
            cls.get_client()
            cls._db = cls._client[DATA_BASE]
        return cls._db

    @classmethod
    def close_connection(cls):
        """MongoDB 클라이언트를 종료"""
        if cls._client:
            cls._client.close()
            print("MongoDB 연결이 종료되었어요")
            cls._client = None
            cls._db = None