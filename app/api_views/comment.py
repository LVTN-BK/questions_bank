from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import COMMENTS, EXAMS, LIKES, REPLY_COMMENTS, SYSTEM, app, comments_db
from fastapi import Depends, Path, status, Query
from fastapi.encoders import jsonable_encoder
from models.db.comment import Comments_DB, Reply_Comments_DB
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

#========================================================
#==================QUESTION_GET_LIST_COMMENT=============
#========================================================
@app.get(
    path='/question_get_list_comment',
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
async def question_get_list_comment(
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
                    'is_removed': False
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
                                "content": 1,
                                'datetime_created': 1,
                                'datetime_updated': 1
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

        comments = comments_db[COMMENTS].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=comments, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================EXAM_GET_LIST_COMMENT===============
#========================================================
@app.get(
    path='/exam_get_list_comment',
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
async def exam_get_list_comment(
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
                    'is_removed': False
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
                                "content": 1,
                                'datetime_created': 1,
                                'datetime_updated': 1
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

        comments = comments_db[COMMENTS].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=comments, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===================GET_LIST_REPLY_COMMENT===============
#========================================================
@app.get(
    path='/get_list_reply_comment',
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
async def get_list_reply_comment(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    comment_id: str = Query(..., description='ID of comment'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    'comment_id': comment_id,
                    'is_removed': False
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
                                "content": 1,
                                'datetime_created': 1,
                                'datetime_updated': 1
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

        comments = comments_db[COMMENTS].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=comments, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
