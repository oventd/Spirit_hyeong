DB(MongoDB 기반)

MongoDB와 연동하여 데이터를 관리하고, UI를 통해 사용자와 상호작용할 수 있는 애플리케이션입니다. 
:db_client: MongoDB를 연결합니다.
:db_crud.py: 데이터를 CRUD(Create, Read, Update, Delete) 작업을 처리하는 다양한 모듈을 포함하고 있습니다. 
:assetmanager.py: UI와 DB 간의 의존성을 분리하는 서비스 계층을 만들어 유지보수성을 높였습니다.

/home/rapa/NA_Spirit/DB/
├── /lib/
│    ├── init.py                # 해당 디렉토리를 패키지로 인식하도록 만드는 역할
│    ├── db_client.py           # MongoDB 연결 관리
│    ├── db_crud.py             # DB 접근을 담당하는 CRUD 함수
/home/rapa/NA_Spirit/gui/
├── /gui/                       # UI 관련 폴더
│    ├── assetmanager.py        # UI와 DB를 분리하는 서비스 계층


DbCrud 주요 메서드

upsert_data(filter_conditions, update_fields)
데이터를 업데이트하거나 존재하지 않으면 새로 삽입합니다.

construct_query_pipeline(filter_conditions=None, sort_by=None, sort_order=None, limit=0, skip=0, fields=None, user_query=None)
MongoDB 쿼리 파이프라인을 생성하여 필터링, 정렬, 페이지네이션을 설정합니다.

find(filter_conditions=None, sort_by=None, sort_order=None, limit=0, skip=0, fields=None)
주어진 조건에 맞는 데이터를 조회합니다.

find_one(object_id, fields=None)
특정 ID에 해당하는 데이터를 조회하여 상세 정보를 반환합니다.

search(filter_conditions=None, limit=0, skip=0, fields=None, sort_by=None, sort_order=None, user_query=None)
검색어 기반으로 데이터를 조회하고, 검색 점수에 따라 정렬합니다.

increment_count(object_id, field)
지정된 자산의 다운로드 수를 증가시킵니다.

delete_one(object_id)
특정 자산을 삭제합니다.


AssetDb 주요 메서드

setup_indexes
자산 컬렉션에 대한 인덱스를 설정합니다.

upsert_asset
자산 데이터를 업데이트하거나 새로 추가합니다.



