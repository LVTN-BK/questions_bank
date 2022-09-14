from app.utils.group_utils.group import get_list_group_member_id
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import USERS_PROFILE, app, user_db
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder

from starlette.responses import JSONResponse



#========================================================
#===============SEARCH_USER_NOT_IN_GROUP=================
#========================================================
@app.get(
    path='/search_user_not_in_group',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ''
        }
    },
    tags=['User - Group']
)
async def search_user_not_in_group(
    group_id: str = Query(..., description='ID of group'),
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: str = Query(default=None, description='search text')
):
    try:
        list_group_members = get_list_group_member_id(group_id=group_id)
        if search:
            query_filter = {
                '$and': [
                    {
                        'user_id': {
                            '$nin': list_group_members
                        }
                    },
                    {
                        '$or': [
                            {
                                'name': {
                                    '$regex': search,
                                    '$options': 'i'
                                }
                            },
                            {
                                'email': {
                                    '$regex': search,
                                    '$options': 'i'
                                }
                            }
                        ]
                    }
                ]
            }             
        else:
            query_filter = {
                'user_id': {
                    '$nin': list_group_members
                }
            }

        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': query_filter
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'name': 1,
                    'email': 1,
                    'avatar': 1
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
                            '$sort': {
                                'name': 1
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

        users_data = user_db[USERS_PROFILE].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=users_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#===================GET_USER_INFO========================
#========================================================
@app.get(
    path='/get_user_info',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ''
        }
    },
    tags=['User']
)
async def get_user_info(
    user_id: str = Query(..., description='ID of user')
):
    try:
        pipeline = [
            {
                '$match': {
                    'user_id': user_id
                }
            },
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
                    },
                    'address': {
                        '$ifNull': ['$address', None]
                    },
                    'birthday': {
                        '$ifNull': ['$birthday', None]
                    },
                    'gender': {
                        '$ifNull': ['$gender', None]
                    },
                    'phone': {
                        '$ifNull': ['$phone', None]
                    },
                }
            }
        ]

        user_data = user_db[USERS_PROFILE].aggregate(pipeline)
        if user_data.alive:
            result_data = user_data.next()
        else:
            msg = 'user not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg},status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

