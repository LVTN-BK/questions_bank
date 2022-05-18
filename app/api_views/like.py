from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from configs.logger import logger
from configs.settings import EXAMS, LIKES, SYSTEM, app, likes_db
from fastapi import Depends, Path, status
from fastapi.encoders import jsonable_encoder
from models.db.like import Likes_DB
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
    data1: DATA_Create_Like,
    data2: dict = Depends(valid_headers)
):
    try:
        # check user
        user = SYSTEM['users'].find_one(
            {
                'email': {
                    '$eq': data2.get('email')
                }
            }
        )
        if not user:
            return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        like = Likes_DB(
            user_id=data2.get('user_id'),
            target_id=data1.get('target_id'),
            target_type=data1.get('target_type'),
        )

        logger().info(f'like: {like}')

        # insert to likes table
        id_like = likes_db[LIKES].insert_one(jsonable_encoder(like)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'like_id': str(id_like)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

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
        # check user
        user = SYSTEM['users'].find_one(
            {
                'email': {
                    '$eq': data2.get('email')
                }
            }
        )
        if not user:
            return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)

        query_unlike = {
            'user_id': data2.get('user_id'),
            'target_id': data1.get('target_id'),
            'target_type': data1.get('target_type')
        }
        
        # remove like record
        likes_db[EXAMS].find_one_and_delete(query_unlike)

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
