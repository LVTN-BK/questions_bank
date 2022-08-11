from datetime import datetime
from enum import unique
from importlib.metadata import metadata
from json import JSONEncoder
from math import ceil
from typing import List, Optional, Union

import pymongo
import requests
from app.utils._header import valid_headers
from app.utils.group_info import (get_one_group_info,
                                  get_one_group_name_and_avatar)
from app.utils.question_utils.question import get_data_and_metadata
from bson import ObjectId
from configs import (GROUP, GROUP_INVITATION, GROUP_JOIN_REQUEST,
                     GROUP_PARTICIPANT, app, group_db)
# Config logging
from configs.logger import logger
from fastapi import (BackgroundTasks, Body, Depends, File, Form, Path, Query,
                     UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.db.group import Group_DB, GroupInvitation, GroupMember
from models.define.group import GroupStatus, GroupType, UpdateGroupImage
from models.request.group import (DATA_Accept_invitation,
                                  DATA_Accept_Join_Request,
                                  DATA_Cancel_invitation,
                                  DATA_Cancel_Join_Request, DATA_Create_Group,
                                  DATA_Delete_Group, DATA_Group_created,
                                  DATA_Group_Label, DATA_Invite_Members,
                                  DATA_Join_Request, DATA_Reject_invitation,
                                  DATA_Reject_Join_Request,
                                  DATA_Remove_Members, DATA_Update_Group,
                                  DATA_Update_Group_Chat,
                                  DATA_Update_Group_image)
# import response models
from models.response import *
from pymongo import ReturnDocument


#=================================================================
#======================SEND_REQUEST_JOIN_GROUP====================
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
async def send_request_join_group(
    data: DATA_Join_Request,
    data2: dict = Depends(valid_headers),
):
    try:
        # Find a group
        query = {'_id': ObjectId(data.group_id)}
        group = group_db[GROUP].find_one(query)
        if group:
            json_data = {
                'group_id': data.group_id,
                'user_id': data2.get('user_id'),
                'datetime_created': datetime.now().timestamp()
            }
            try:
                request_id = group_db[GROUP_JOIN_REQUEST].insert_one(json_data).inserted_id
            except Exception as e:
                logger().error(e)
                msg = 'already send join request'
                return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


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
async def group_accept_request_join_group(
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
        query = {'_id': ObjectId(request_join.get('group_id'))}
        group = group_db[GROUP].find_one(query,{'owner_id': 1})
        logger().info(f'group: {group}')
        if group:
            #check owner of group
            if data2.get('user_id') != group.get('owner_id'):
                return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)
            
            #add to group members
            mem_data = GroupMember(
                group_id= request_join.get('group_id'),
                user_id= request_join.get('user_id'),
                datetime_created= datetime.now().timestamp()
            )
            request_id = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(mem_data)).inserted_id

            #remove request join
            group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

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
async def group_reject_request_join_group(
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
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

        # Find a group
        query = {'_id': ObjectId(request_join.get('group_id'))}
        group = group_db[GROUP].find_one(query,{'owner_id': 1})
        if group:
            #check owner of group
            if data2.get('user_id') != group.get('owner_id'):
                return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

            #remove request join
            group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

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
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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
    '/group_list_request_join_group',
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
    group_id: str = Query(..., description='id of group'),
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

#=========================NEED_TO_FIX=============================
#====================USER_LIST_REQUEST_JOIN_GROUP=================
#=================================================================
@app.get(
    '/user_list_request_join_group',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='list of requests to join the group that the user has submitted',
    tags=['Group - Request Join']
)
async def user_list_request_join_group(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    data2: dict = Depends(valid_headers),
    # user_id: str = Path(..., description='id of user'),
):
    try:
        #get list request
        query_request = {
            'user_id': data2.get('user_id')
        }
        num_skip = (page - 1)*limit
        list_request = group_db[GROUP_JOIN_REQUEST].find(query_request).skip(num_skip).limit(limit)
        result = []
        if list_request.count(True):
            for request_join in list_request:
                request_join['_id'] = str(request_join['_id'])
                group_info = get_one_group_name_and_avatar(group_id=request_join['group_id'])
                if group_info:
                    request_join['group'] = group_info
                    del request_join['group_id']
                    del request_join['user_id']
                    result.append(request_join)
                #remove request if group not found
                ##################################

        num_request_join = group_db[GROUP_JOIN_REQUEST].find(query_request).count()
        logger().info(f'num request join: {num_request_join}')
        num_pages = ceil(num_request_join/limit)

        meta_data = {
            'count': list_request.count(True),
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }
        return JSONResponse(content={'status': 'success', 'data': result, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
