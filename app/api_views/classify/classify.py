import copy
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.classify_utils.classify import check_permission_with_chapter, check_permission_with_class, check_permission_with_subject
from configs.logger import logger
from configs.settings import (CHAPTER, CLASS, QUESTIONS, SUBJECT, TAG_COLLECTION,
                              app, classify_db, questions_db)
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from models.define.classify import ClassifyOwnerType
from models.request.classify import DATA_Create_Chapter, DATA_Create_Class, DATA_Create_Subject, DATA_Delete_Chapter, DATA_Delete_Class, DATA_Delete_Subject, DATA_Update_Subject, DATA_Update_chapter, DATA_Update_class

from starlette.responses import JSONResponse


#========================================================
#======================UPDATE_SUBJECT====================
#========================================================
@app.put(
    path='/update_subject',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def update_subject(
    data1: DATA_Update_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        if not check_permission_with_subject(user_id=data2.get('user_id'), subject_id=data1.subject_id):
            raise Exception('user not have permission with subject!')

        #insert into subjects db
        subject_data = classify_db[SUBJECT].find_one_and_update(
            {
                '_id': ObjectId(data1.subject_id),
                # 'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'name': data1.name
                }
            }
        )
        if subject_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'subject not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#======================DELETE_SUBJECT====================
#========================================================
@app.delete(
    path='/delete_subject',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def delete_subject(
    data1: DATA_Delete_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        # find if have question use this subject
        subject_usage = questions_db[QUESTIONS].find_one(
            {
                'subject_id': data1.subject_id
            }
        )
        if subject_usage:
            msg = 'subject is in-use, can\'t delete it!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        subject_data = classify_db[SUBJECT].find_one_and_delete(
            {
                '_id': ObjectId(data1.subject_id),
                'user_id': data2.get('user_id')
            }
        )
        if subject_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'subject not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#======================UPDATE_CLASS======================
#========================================================
@app.put(
    path='/update_class',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def update_class(
    data1: DATA_Update_class,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of class
        if not check_permission_with_class(user_id=data2.get('user_id'), class_id=data1.class_id):
            raise Exception('user not have permission with class!')
        
        class_data = classify_db[CLASS].find_one_and_update(
            {
                '_id': ObjectId(data1.class_id),
                # 'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'name': data1.name
                }
            }
        )
        if class_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'class not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=======================DELETE_CLASS=====================
#========================================================
@app.delete(
    path='/delete_class',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def delete_class(
    data1: DATA_Delete_Class,
    data2: dict = Depends(valid_headers)
):
    try:
        # find if have question use this class
        class_usage = questions_db[QUESTIONS].find_one(
            {
                'class_id': data1.class_id
            }
        )
        if class_usage:
            msg = 'class is in-use, can\'t delete it!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        class_data = classify_db[CLASS].find_one_and_delete(
            {
                '_id': ObjectId(data1.class_id),
                'user_id': data2.get('user_id')
            }
        )
        if class_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'class not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=====================UPDATE_CHAPTER=====================
#========================================================
@app.put(
    path='/update_chapter',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def update_chapter(
    data1: DATA_Update_chapter,
    data2: dict = Depends(valid_headers)
):
    try:
        if not check_permission_with_chapter(user_id=data2.get('user_id'), chapter_id=data1.chapter_id):
            raise Exception('user not have permission with chapter!')
        
        chapter_data = classify_db[CHAPTER].find_one_and_update(
            {
                '_id': ObjectId(data1.chapter_id),
                # 'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'name': data1.name
                }
            }
        )
        if chapter_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'chapter not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#======================DELETE_CHAPTER====================
#========================================================
@app.delete(
    path='/delete_chapter',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def delete_chapter(
    data1: DATA_Delete_Chapter,
    data2: dict = Depends(valid_headers)
):
    try:
        # find if have question use this class
        chapter_usage = questions_db[QUESTIONS].find_one(
            {
                'chapter_id': data1.chapter_id
            }
        )
        if chapter_usage:
            msg = 'chapter is in-use, can\'t delete it!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        chapter_data = classify_db[CHAPTER].find_one_and_delete(
            {
                '_id': ObjectId(data1.chapter_id),
                'user_id': data2.get('user_id')
            }
        )
        if chapter_data:
            return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
        else:
            msg = 'chapter not found!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#==========================GET_TAGS======================
#========================================================
@app.get(
    path='/get_tags',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ''
        }
    },
    tags=['classify']
)
async def get_tags(
    search_text: str = Query(default=None, description='search text')
):
    try:
        if search_text:
            query_filter = {
                'name': {
                    '$regex': search_text,
                    '$options': 'i'
                }
            }
        else:
            query_filter = {}

        pipeline = [
            {
                '$match': query_filter
            },
            {
                '$project': {
                    '_id': 0,
                    'id': {
                        '$toString': '$_id'
                    },
                    'name': 1,
                }
            },
            {
                '$group': {
                    '_id': None,
                    'data': {
                        '$push': '$$ROOT'
                    }
                }
            }
        ]

        tags_data = classify_db[TAG_COLLECTION].aggregate(pipeline)
        result = []
        if tags_data.alive:
            result = tags_data.next().get('data')

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

