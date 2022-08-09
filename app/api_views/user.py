import copy
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.group_utils.group import get_list_group_member_id
from app.utils.question_utils.question import get_data_and_metadata
from configs.logger import logger
from configs.settings import USERS_PROFILE, app, user_db
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from models.request.classify import DATA_Create_Chapter, DATA_Create_Class, DATA_Create_Subject

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
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

