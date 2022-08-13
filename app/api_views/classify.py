import copy
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from configs.logger import logger
from configs.settings import (CHAPTER, CLASS, SUBJECT, TAG_COLLECTION,
                              app, classify_db)
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from models.request.classify import DATA_Create_Chapter, DATA_Create_Class, DATA_Create_Subject

from starlette.responses import JSONResponse


#========================================================
#======================CREATE_SUBJECT====================
#========================================================
@app.post(
    path='/create_subject',
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
async def create_subject(
    data1: DATA_Create_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        subject_data = Subjects_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'subject_id': str(subject_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=======================CREATE_CLASS=====================
#========================================================
@app.post(
    path='/create_class',
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
async def create_class(
    data1: DATA_Create_Class,
    data2: dict = Depends(valid_headers)
):
    try:
        class_data = Class_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            subject_id=data1.subject_id,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        class_id = classify_db[CLASS].insert_one(jsonable_encoder(class_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'class_id': str(class_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#======================CREATE_CHAPTER====================
#========================================================
@app.post(
    path='/create_chapter',
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
async def create_chapter(
    data1: DATA_Create_Chapter,
    data2: dict = Depends(valid_headers)
):
    try:
        chapter_data = Chapters_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            class_id=data1.class_id,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        chapter_id = classify_db[CHAPTER].insert_one(jsonable_encoder(chapter_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'chapter_id': str(chapter_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#========================GET_CLASSIFY====================
#========================================================
@app.get(
    path='/get_classify',
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
async def get_classify(
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    'user_id': data2.get('user_id')
                }
            },
            {
                '$addFields': {
                    'subject_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'localField': 'subject_id',
                    'foreignField': 'subject_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'class_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'localField': 'class_id',
                                'foreignField': 'class_id',
                                'pipeline': [
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': {
                                                '$toString': '$_id'
                                            },
                                            'name': 1
                                        }
                                    },
                                    {
                                        '$sort': {
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'chapters'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': {
                                    '$getField': 'class_id'
                                },
                                'name': 1,
                                'chapters': 1
                            }
                        }      
                    ],
                    'as': 'classes'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'id': {
                        '$getField': 'subject_id'
                    },
                    'name': 1,
                    'classes': 1
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

        all_subject = classify_db[SUBJECT].aggregate(pipeline)
        result = []
        if all_subject.alive:
            result = all_subject.next().get('data')

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
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

