from app.utils._header import valid_headers
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import EXAMS, LIKES, SYSTEM, app, likes_db
from fastapi import Depends, Path, status, Query, BackgroundTasks
from models.define.target import ManageTargetType
from starlette.responses import JSONResponse


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
