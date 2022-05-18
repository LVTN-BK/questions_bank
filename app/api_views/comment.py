from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from configs.logger import logger
from configs.settings import COMMENTS, EXAMS, LIKES, REPLY_COMMENTS, SYSTEM, app, comments_db
from fastapi import Depends, Path, status
from fastapi.encoders import jsonable_encoder
from models.db.comment import Comments_DB, Reply_Comments_DB
from models.request.comment import DATA_Create_Comment, DATA_Create_Reply_Comment, DATA_Remove_Comment, DATA_Remove_Reply_Comment
from models.request.like import DATA_Create_Like, DATA_Unlike
from starlette.responses import JSONResponse


#========================================================
#===================CREATE_COMMENT=======================
#========================================================
@app.post(
    path='/create_comment',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['comments']
)
async def create_comment(
    data1: DATA_Create_Comment,
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
        
        comment = Comments_DB(
            user_id=data2.get('user_id'),
            target_id=data1.get('target_id'),
            target_type=data1.get('target_type'),
            content=data1.get('content'),
        )

        logger().info(f'comment: {comment}')

        # insert to comments table
        id_comment = comments_db[COMMENTS].insert_one(jsonable_encoder(comment)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'comment_id': str(id_comment)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#================CREATE_REPLY_COMMENT====================
#========================================================
@app.post(
    path='/create_reply_comment',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['comments']
)
async def create_reply_comment(
    data1: DATA_Create_Reply_Comment,
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
        
        reply_comment = Reply_Comments_DB(
            user_id=data2.get('user_id'),
            comment_id=data1.get('comment_id'),
            content=data1.get('content'),
        )

        logger().info(f'reply_comment: {reply_comment}')

        # insert to comments table
        id_reply_comment = comments_db[REPLY_COMMENTS].insert_one(jsonable_encoder(reply_comment)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'reply_comment_id': str(id_reply_comment)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=====================REMOVE_COMMENT=====================
#========================================================
@app.post(
    path='/remove_comment',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['comments']
)
async def remove_comment(
    data1: DATA_Remove_Comment,
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

        query_remove_comment = {
            '_id': ObjectId(data1.get('comment_id')),
            'user_id': data2.get('user_id')
        }
        
        # remove comment record
        comments_db[COMMENTS].find_one_and_delete(query_remove_comment)

        # delete reply comment
        query_remove_reply_comment = {
            'comment_id': data1.get('comment_id')
        }
        comments_db[REPLY_COMMENTS].delete_many(query_remove_reply_comment)

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#==================REMOVE_REPLY_COMMENT==================
#========================================================
@app.post(
    path='/remove_comment',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['comments']
)
async def remove_reply_comment(
    data1: DATA_Remove_Reply_Comment,
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

        query_remove_reply_comment = {
            '_id': ObjectId(data1.get('reply_comment_id')),
            'user_id': data2.get('user_id')
        }
        
        # remove comment record
        comments_db[COMMENTS].find_one_and_delete(query_remove_reply_comment)

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
