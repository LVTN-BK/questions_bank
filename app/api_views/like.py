from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import EXAMS, LIKES, SYSTEM, app, likes_db
from fastapi import Depends, Path, status, Query
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
    data1: DATA_Create_Like,
    data2: dict = Depends(valid_headers)
):
    try:        
        like = Likes_DB(
            user_id=data2.get('user_id'),
            target_id=data1.target_id,
            target_type=data1.target_type,
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


#========================================================
#==================QUESTION_GET_LIST_LIKE================
#========================================================
@app.get(
    path='/question_get_list_like',
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
async def question_get_list_like(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    question_id: str = Query(..., description='ID of question'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    'target_id': question_id,
                    'target_type': ManageTargetType.QUESTION,
                }
            },
            {
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'pipeline': [
                        {
                            '$project': {
                                '_id': 0,
                                'user_id': 1,
                                'name': {
                                    '$ifNull': ['$name', None]
                                },
                                'email': {
                                    '$ifNull': ['$email', None]
                                },
                                'avatar': {
                                    '$ifNull': ['$avatar', None]
                                }
                            }
                        }
                    ],
                    'as': 'author_data'
                }
            },
            {
                '$set': {
                    'author_info': {
                        '$ifNull': [{'$first': '$author_data'}, None]
                    }
                }
            },                  
            { 
                '$facet' : {
                    'metadata': [ 
                        { 
                            '$count': "total" 
                        }, 
                        { 
                            '$addFields': { 
                                'page': {
                                    '$toInt': {
                                        '$ceil': {
                                            '$divide': ['$total', limit]
                                        }
                                    }
                                }
                            } 
                        } 
                    ],
                    'data': [ 
                        {
                            '$project': {
                                '_id': 0,
                                'id': {
                                    '$toString': '$_id'
                                },
                                "author_info": 1,
                                'datetime_created': 1,
                            }
                        },
                        {
                            '$sort': {
                                'datetime_created': -1
                            }
                        },
                        { 
                            '$skip': num_skip 
                        },
                        { 
                            '$limit': limit 
                        } 
                    ] # add projection here wish you re-shape the docs
                } 
            },
            {
                '$unwind': '$metadata'
            },
        ]

        likes = likes_db[LIKES].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=likes, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================EXAM_GET_LIST_LIKE===============
#========================================================
@app.get(
    path='/exam_get_list_like',
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
async def exam_get_list_like(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    exam_id: str = Query(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    'target_id': exam_id,
                    'target_type': ManageTargetType.EXAM,
                }
            },
            {
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'pipeline': [
                        {
                            '$project': {
                                '_id': 0,
                                'user_id': 1,
                                'name': {
                                    '$ifNull': ['$name', None]
                                },
                                'email': {
                                    '$ifNull': ['$email', None]
                                },
                                'avatar': {
                                    '$ifNull': ['$avatar', None]
                                }
                            }
                        }
                    ],
                    'as': 'author_data'
                }
            },
            {
                '$set': {
                    'author_info': {
                        '$ifNull': [{'$first': '$author_data'}, None]
                    }
                }
            },                  
            { 
                '$facet' : {
                    'metadata': [ 
                        { 
                            '$count': "total" 
                        }, 
                        { 
                            '$addFields': { 
                                'page': {
                                    '$toInt': {
                                        '$ceil': {
                                            '$divide': ['$total', limit]
                                        }
                                    }
                                }
                            } 
                        } 
                    ],
                    'data': [ 
                        {
                            '$project': {
                                '_id': 0,
                                'id': {
                                    '$toString': '$_id'
                                },
                                "author_info": 1,
                                'datetime_created': 1,
                            }
                        },
                        {
                            '$sort': {
                                'datetime_created': -1
                            }
                        },
                        { 
                            '$skip': num_skip 
                        },
                        { 
                            '$limit': limit 
                        } 
                    ] # add projection here wish you re-shape the docs
                } 
            },
            {
                '$unwind': '$metadata'
            },
        ]

        likes = likes_db[LIKES].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=likes, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



