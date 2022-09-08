from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import COMMENTS, EXAMS, LIKES, REPLY_COMMENTS, SYSTEM, app, comments_db
from fastapi import Depends, Path, status, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from models.db.comment import Comments_DB, Reply_Comments_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.target import ManageTargetType
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
@SendNotiDecoratorsApi.create_comment
async def create_comment(
    background_tasks: BackgroundTasks,
    data: DATA_Create_Comment,
    data2: dict = Depends(valid_headers)
):
    try:
        comment = Comments_DB(
            user_id=data2.get('user_id'),
            target_id=data.target_id,
            target_type=data.target_type,
            content=data.content,
            datetime_created=datetime.now().timestamp()
        )

        logger().info(f'comment: {comment}')

        # insert to comments table
        id_comment = comments_db[COMMENTS].insert_one(jsonable_encoder(comment)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'comment_id': str(id_comment)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

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
@SendNotiDecoratorsApi.create_reply_comment
async def create_reply_comment(
    background_tasks: BackgroundTasks,
    data: DATA_Create_Reply_Comment,
    data2: dict = Depends(valid_headers)
):
    try:
        reply_comment = Reply_Comments_DB(
            user_id=data2.get('user_id'),
            comment_id=data.comment_id,
            content=data.content,
            datetime_created=datetime.now().timestamp()
        )

        logger().info(f'reply_comment: {reply_comment}')

        # insert to comments table
        id_reply_comment = comments_db[REPLY_COMMENTS].insert_one(jsonable_encoder(reply_comment)).inserted_id

        return JSONResponse(content={'status': 'success', 'data': {'reply_comment_id': str(id_reply_comment)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=====================REMOVE_COMMENT=====================
#========================================================
@app.delete(
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
        # remove comment record
        comment_data = comments_db[COMMENTS].find_one_and_update(
            {
                '_id': ObjectId(data1.comment_id),
                'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'is_removed': True
                }
            }
        )

        if comment_data:
            # delete reply comment
            comments_db[REPLY_COMMENTS].update_many(
                {
                    'comment_id': data1.comment_id
                },
                {
                    '$set': {
                        'is_removed': True
                    }
                }
            )

            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'comment not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg},status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#==================REMOVE_REPLY_COMMENT==================
#========================================================
@app.delete(
    path='/remove_reply_comment',
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
        # remove comment record
        comment_data = comments_db[REPLY_COMMENTS].find_one_and_update(
            {
                '_id': ObjectId(data1.reply_comment_id),
                'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'is_removed': True
                }
            }
        )

        if comment_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'comment not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg},status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
