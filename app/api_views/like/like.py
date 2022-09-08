from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import EXAMS, LIKES, SYSTEM, app, likes_db
from fastapi import Depends, Path, status, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from models.db.like import Likes_DB
from models.define.target import ManageTargetType
from models.request.like import DATA_Create_Like, DATA_Unlike
from starlette.responses import JSONResponse


#========================================================
#=====================CREATE_LIKE========================
#========================================================
@app.post(
    path='/create_like',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['likes']
)
async def create_like(
    background_tasks: BackgroundTasks,
    data: DATA_Create_Like,
    data2: dict = Depends(valid_headers)
):
    try:        
        like = Likes_DB(
            user_id=data2.get('user_id'),
            target_id=data.target_id,
            target_type=data.target_type,
            datetime_created=datetime.now().timestamp()
        )

        logger().info(f'like: {like}')

        # insert to likes table
        id_like = likes_db[LIKES].insert_one(jsonable_encoder(like)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'like_id': str(id_like)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=========================UNLIKE=========================
#========================================================
@app.post(
    path='/unlike',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['likes']
)
async def unlike(
    data1: DATA_Unlike,
    data2: dict = Depends(valid_headers)
):
    try:
        query_unlike = {
            'user_id': data2.get('user_id'),
            'target_id': data1.target_id,
            'target_type': data1.target_type
        }
        
        # remove like record
        likes_db[LIKES].find_one_and_delete(query_unlike)

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



