"""
Spirit 전체 상수 파일입니다.
"""
# DB 커넥션 상수
MONGODB_ADRESS = "mongodb://192.168.5.10:27017" # mongoDB 주소
DATA_BASE = "spiritDatabase" # 접속할 데이터 베이스 명
USER_COLLECTION = "test" # 데이터 베이스에서 접속할 컬렉션 명


# DB 데이터 key값 상수
OBJECT_ID = "_id"  # ObjectId('') 값
ASSET_ID = "asset_id"  # asset_id 값
NAME = "name"  # asset name
DESCRIPTION = "description"  # description 값
ASSET_TYPE = "asset_type"  # asset_type 값
CATEGORY = "category"  # category 값
STYLE = "style"  # style 값
RESOLUTION = "resolution"  # resolution 값
FILE_FORMAT = "file_format"  # file_format 값
SIZE = "size"  # size 값
LICENSE_TYPE = "license_type"  # license_type 값
CREATOR_ID = "creator_id"  # creator_id 값
CREATOR_NAME = "creator_name"  # creator_name 값
DOWNLOADS = "downloads"  # downloads 값
CREATED_AT = "created_at"  # created_at 값
UPDATED_AT = "updated_at"  # updated_at 값
PRICE = "price"  # price 값
PREVIEW_URL = "preview_url"  # preview_url 값

SEARCH_FIELDS = ["_id", "name", "description", "asset_type", "category", 
"style", "resolution", "file_format", "size", "license_type",
"creator_id", "creator_name", "downloads", "price", 
"image_url","source_url","video_url", "preview_url",
"created_at", "updated_at"]


# 버려도 되는 친구
DETAIL_URL = "detail_url"  # particular_url 값
PRESETTING_URL1 = "presetting_url1"  # presetting_url1 값
PRESETTING_URL2 = "presetting_url2"  # presetting_url2 값
PRESETTING_URL3 = "presetting_url3"  # presetting_url3 값
TURNAROUND_URL = "turnaround_url" # turnaround_url 값
RIG_URL = "rig_url" # rig_url 값
APPLY_HDRI = "applyhdri_url" # applyhdri_url 값
HDRI_URL = "hdri_url" # hdri_url 값
MATERIAL_URLS = "material_urls" # material_urls 값

# DB 인덱싱 정의 상수(메타 데이터)
SCORE = "score"
TEXT = "text"

# logger 관련 상수
LOGGER_NAME = "db_crud" # DbCrud(객체 생성용) 로거 이름
DB_LOGGER_DIR = "/nas/spirit/DB/db_logger" # 로거 저장 경로
ASSET_LOGGER_NAME = "user_db" # 로거 저장 이름
ASSET_LOGGER_DIR = "/nas/spirit/DB/log/asset_library.log" # 에셋 로거 저장 경로


# ux logger 관련 상수
UX_Like_ASSET_LOGGER_NAME = "ux_like_asset" # user_ux(객체 생성용) 로거 이름
UX_Like_ASSET_LOGGER_DIR = "/nas/spirit/gui/log/like_asset_logger.log" # 로거 저장 이름

UX_DOWNLOAD_LOGGER_NAME = "ux_download" # user_ux(객체 생성용) 로거 이름
UX_DOWNLOAD_LOGGER_DIR = "/nas/spirit/gui/log/download_logger.log" # 로거 저장 이름

# Shotgrid Pipeline Step 상수
MODELING = 'Model'
RIGGING = 'Rig'
LOOKDEV = 'Lookdev'
MATCHMOVE = 'Matchmove'
LAYOUT = 'Layout'
ANIMATING = 'Animation'
LIGHTING = 'Light'
COMPOSITING = 'Comp'


# Open step 상수 --- 바뀨기
STEP_PATH = '/home/rapa/NA_Spirit/open/step'
UTILS_PATH = '/home/rapa/NA_Spirit/utils'
# RIGG = "rig"
# GEO = "geo"
# ENV = "env"
# LOW = "Low"
# HIGH = "High"
# ANIM_CAM = "anim_cam"
# CAMERA1 = "camera1"
# TERRAIN ="terrain"
# CAMERA = "camera"
# CHAR = "char"

# Shotgrid Pipeline Step Shot 상수
MDL = 'MDL' # Model
RIG = 'RIG' # Rig
LDV = 'LDV' # Lookdev
MMV = 'MMV' # Matchmove
LAY = 'LAY' # Layout
ANM = 'ANM' # Animation
LGT = 'LGT' # Light
CMP = 'CMP' # Compositing


#Shotgrid Project 상수
SERVER_PATH = 'https://5thacademy.shotgrid.autodesk.com'
SCRIPT_NAME = 'nayeon_key'
API_KEY = 'h0mvmfnhuochunhzpgR~zlpur'


#Shotgrid Project 상수
SERVER_PATH = 'https://5thacademy.shotgrid.autodesk.com'
SCRIPT_NAME = 'nayeon_key'
API_KEY = 'h0mvmfnhuochunhzpgR~zlpur'

STEP_SHORT_DICT = {
    MODELING: MDL,
    RIGGING: RIG,
    LOOKDEV: LDV,
    MATCHMOVE: MMV,
    LAYOUT: LAY,
    ANIMATING: ANM,
    LIGHTING: LGT,
    COMPOSITING: CMP
}
SHORT_STEP_DICT = {
    MDL : MODELING,
    RIG : RIGGING,
    LDV : LOOKDEV,
    MMV : MATCHMOVE,
    LAY : LAYOUT,
    ANM : ANIMATING,
    LGT : LIGHTING,
    CMP : COMPOSITING
}
#   "Rig": {
#     "module": "open_rigging",
#     "class": "RiggingStep",
#     "path": "/home/rapa/NA_Spirit/open/step/open_rigging.py"
#   }  ,
#     },
#   "Matchmove": {
#     "module": "open_matchmove",
#     "class": "MatchMoveStep",
#     "path": "/home/rapa/NA_Spirit/open/step/open_matchmove.py"
#   },
#   "Layout": {
#     "module": "open_layout",
#     "class": "LayoutStep",
#     "path": "/home/rapa/NA_Spirit/open/step/open_layout.py"
#   },
#   "Animation": {
#     "module": "open_animating",
#     "class": "AnimatingStep",
#     "path": "/home/rapa/NA_Spirit/open/step/open_animating.py"
#   },
#   "Light": {
#     "module": "open_lighting",
#     "class": "LightingStep",
#     "path": "/home/rapa/NA_Spirit/open/step/open_lighting.py"
#   }  