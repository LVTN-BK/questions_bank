from datetime import datetime
from app.utils._header import valid_headers
from app.utils.group_utils.group import check_group_exist, check_owner_of_group
from app.utils.question_utils.question import get_data_and_metadata
from bson import ObjectId
from configs import (GROUP, GROUP_JOIN_REQUEST,
                     GROUP_PARTICIPANT, app, group_db)
# Config logging
from configs.logger import logger
from fastapi import (BackgroundTasks, Depends, Path, Query,
                     status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.db.group import GroupMember
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.group import GroupType
from models.request.group import (DATA_Accept_Join_Request,
                                  DATA_Cancel_Join_Request,
                                  DATA_Join_Request,
                                  DATA_Reject_Join_Request)
# import response models
from models.response import *


#=================================================================
#====================USER_SEND_REQUEST_JOIN_GROUP=================
#=================================================================
@app.post(
    '/request_join_group',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='send request to join group',
    tags=['Group - Request Join']
)
@SendNotiDecoratorsApi.user_request_join_group
async def send_request_join_group(
    background_tasks: BackgroundTasks,
    data: DATA_Join_Request,
    data2: dict = Depends(valid_headers),
):
    try:
        # Find a group
        group = check_group_exist(group_id=data.group_id)
        if group:
            # check group is public
            if group.get('group_type') == GroupType.PUBLIC:
                #add to group members
                mem_data = GroupMember(
                    group_id= data.group_id,
                    user_id= data2.get('user_id'),
                    datetime_created= datetime.now().timestamp()
                )
                participant_id = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(mem_data)).inserted_id

                msg = 'join group successful!!!'
                return JSONResponse(content={'status': 'success', 'msg': msg}, status_code=status.HTTP_200_OK)

            json_data = {
                'group_id': data.group_id,
                'user_id': data2.get('user_id'),
                'datetime_created': datetime.now().timestamp()
            }
            try:
                request_id = group_db[GROUP_JOIN_REQUEST].insert_one(json_data).inserted_id
            except Exception as e:
                logger().error(e)
                raise Exception('already send join request')

            return JSONResponse(content={'status': 'success', 'request_id': str(request_id)}, status_code=status.HTTP_200_OK)
        else:
            msg='group not found!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#==================GROUP_ACCEPT_REQUEST_JOIN_GROUP================
#=================================================================
@app.post(
    '/accept_request_join_group',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='accept request join group',
    tags=['Group - Request Join']
)
@SendNotiDecoratorsApi.group_accept_request_join
async def group_accept_request_join_group(
    background_tasks: BackgroundTasks,
    data: DATA_Accept_Join_Request,
    data2: dict = Depends(valid_headers),
):
    try:
        #find request
        query_request = {
            '_id': ObjectId(data.request_id)
        }
        request_join = group_db[GROUP_JOIN_REQUEST].find_one(query_request,{'group_id':1, 'user_id':1})
        logger().info(f'request join: {request_join}')
        if not request_join:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

        # Find a group
        group = check_group_exist(group_id=request_join.get('group_id'))
        if group:
            #check owner of group
            if not check_owner_of_group(user_id=data2.get('user_id'), group_id=request_join.get('group_id')):
                raise Exception('user is not owner of group!')
            
            #add to group members
            mem_data = GroupMember(
                group_id= request_join.get('group_id'),
                user_id= request_join.get('user_id'),
                datetime_created= datetime.now().timestamp()
            )
            request_id = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(mem_data)).inserted_id

            # #remove request join
            # group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

            data = {
                'group_id': request_join.get('group_id'),
                'group_name': group.get('group_name'),
                'member_id': request_join.get('user_id'),
            }
            return JSONResponse(content={'status': 'success', 'data': data}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#==================GROUP_REJECT_REQUEST_JOIN_GROUP================
#=================================================================
@app.post(
    '/reject_request_join_group',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='reject request join group',
    tags=['Group - Request Join']
)
@SendNotiDecoratorsApi.group_reject_request_join
async def group_reject_request_join_group(
    background_tasks: BackgroundTasks,
    data: DATA_Reject_Join_Request,
    data2: dict = Depends(valid_headers),
):
    try:
        #find request
        query_request = {
            '_id': ObjectId(data.request_id)
        }
        request_join = group_db[GROUP_JOIN_REQUEST].find_one(query_request,{'group_id':1, 'user_id':1})
        if not request_join:
            msg = 'request join not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # Find a group
        group = check_group_exist(group_id=request_join.get('group_id'))
        if group:
            #check owner of group
            if not check_owner_of_group(user_id=data2.get('user_id'), group_id=data.group_id):
                raise Exception('user is not owner of group!')

            # #remove request join
            # group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

            data = {
                'group_id': request_join.get('group_id'),
                'group_name': group.get('group_name'),
                'member_id': request_join.get('user_id'),
            }
            return JSONResponse(content={'status': 'success', 'data': data}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#===================USER_CANCEL_REQUEST_JOIN_GROUP================
#=================================================================
@app.post(
    '/user_cancel_request_join_group',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='user cancel request join group',
    tags=['Group - Request Join']
)
async def user_cancel_request_join_group(
    data: DATA_Cancel_Join_Request,
    data2: dict = Depends(valid_headers),
):
    try:
        #find request
        query_request = {
            '$and': [
                {
                    'group_id': data.group_id
                },
                {
                    'user_id': data2.get('user_id')
                }
            ]
        }
        request_join = group_db[GROUP_JOIN_REQUEST].find_one(query_request,{'group_id':1, 'user_id':1})
        if not request_join:
            msg = 'request join not found!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        #delete request join
        result = group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=================GROUP_LIST_REQUEST_JOIN_GROUP===================
#=================================================================
@app.get(
    '/group_list_request_join_group/{group_id}',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='list of users who sent a request to join the group',
    tags=['Group - Request Join']
)
async def group_list_request_join_group(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    # user_id: str = Query(..., description='id of user(owner of group)'),
    group_id: str = Path(..., description='id of group'),
    data2: dict = Depends(valid_headers),
):
    try:
        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': {
                    'group_id': group_id
                }
            },
            {
                '$set': {
                    'group_id_obj': {
                        '$toObjectId': '$group_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'group',
                    'localField': 'group_id_obj',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$project': {
                                '_id': 0,
                                'group_id': {
                                    '$toString': '$_id'
                                },
                                'group_name': 1,
                                'group_type': 1,
                                'group_cover_image': 1
                            }
                        }
                    ],
                    'as': 'group_info'
                }
            },
            {
                '$unwind': '$group_info'
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
                                'name': 1,
                                'avatar': 1
                            }
                        }
                    ],
                    'as': 'user_info'
                }
            },
            {
                '$unwind': '$user_info'
            },
            {
                '$project': {
                    '_id': 0,
                    'id': {
                        '$toString': '$_id'
                    },
                    'group_info': 1,
                    'user_info': 1,
                    'datetime_created': 1
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
                                'id': 1
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
        
        request_join_data = group_db[GROUP_JOIN_REQUEST].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=request_join_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
