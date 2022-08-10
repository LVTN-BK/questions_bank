#  Copyright (c) 2021.
from datetime import datetime
from enum import unique
from importlib.metadata import metadata
from json import JSONEncoder
from math import ceil
from typing import List, Optional, Union
from app.utils.question_utils.question import get_data_and_metadata
from models.db.group import Group_DB, GroupInvitation, GroupMember

import pymongo
import requests
from bson import ObjectId
from fastapi import BackgroundTasks, Depends, Path, Query, Body, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument
from app.utils.group_info import get_one_group_info, get_one_group_name_and_avatar

from configs import GROUP, GROUP_INVITATION, GROUP_JOIN_REQUEST, GROUP_PARTICIPANT, app, group_db
from models.define.group import GroupStatus, GroupType, UpdateGroupImage
from models.request.group import DATA_Accept_Join_Request, DATA_Accept_invitation, DATA_Cancel_Join_Request, DATA_Cancel_invitation, DATA_Create_Group, DATA_Delete_Group, DATA_Group_Label, DATA_Group_created, DATA_Invite_Members, DATA_Join_Request, DATA_Reject_Join_Request, DATA_Reject_invitation, DATA_Remove_Members, DATA_Update_Group, DATA_Update_Group_Chat, DATA_Update_Group_image
# import response models
from models.response import *

# Config logging
from configs.logger import logger
from fastapi.encoders import jsonable_encoder
from app.utils._header import valid_headers




#==================================================================
#=========================CREATE_GROUP=============================
#==================================================================
@app.post(
    '/create_group',
    responses={
        status.HTTP_200_OK: {
            'model': CreateGroupResponse200
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': CreateGroupResponse400
        }
    },
    description='Create group',
    tags=['Group']
)
async def create_group(
    data: DATA_Create_Group,
    data2: dict = Depends(valid_headers)
):
    try:
        logger().info(data.json())
        
        group_data = Group_DB(
            owner_id=data2.get('user_id'),
            group_name=data.group_name,
            group_description=data.group_description,
            group_type=data.group_type,
            # group_avatar=data.group_avatar,
            group_cover_image=data.group_cover_image
        )
        json_data = jsonable_encoder(group_data)

        group_id = group_db[GROUP].insert_one(json_data).inserted_id
        
        logger().info(group_id)

        #insert menber in group participant collection
        mem = GroupMember(
            user_id = data2.get('user_id'),
            group_id = str(group_id),
            is_owner = True,
            datetime_created = datetime.now().timestamp()
        )
        
        insert = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(mem))


        return JSONResponse(content={'status': 'Done', 'data':{'group_id': str(group_id)}}, status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

#==================================================================
#=========================UPDATE_GROUP=============================
#==================================================================
@app.post(
    '/update_group',
    responses={
        status.HTTP_200_OK: {
            'model': UpdateGroupResponse200
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': UpdateGroupResponse400
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UpdateGroupResponse403
        },
        status.HTTP_404_NOT_FOUND: {
            'model': UpdateGroupResponse404
        }
    },
    description='Update group',
    tags=['Group']
)
async def update_group(
    data: DATA_Update_Group,
    data2: dict = Depends(valid_headers)
):
    try:
        # Find a group
        query = {'_id': ObjectId(data.group_id)}
        group = group_db.get_collection('group').find_one(query)
        if group:
            # check owner of group
            if group.get('owner_id') != data2.get('user_id'):
                content = {'status': 'Forbidden'}
                return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

            update_data = {}

            if data.group_name is not None:
                update_data['group_name'] = data.group_name
            if data.group_description is not None:
                update_data['group_description'] = data.group_description
            if data.group_type is not None:
                update_data['group_type'] = data.group_type
            if data.group_cover_image is not None:
                update_data['group_cover_image'] = data.group_cover_image
         
            # #Group_avatar
            # if data.group_avatar is not None:
            #     update_data['group_avatar'] = data.group_avatar
            
            # #Group_cover_image
            # if data.group_cover_image is not None:
            #     update_data['group_cover_image'] = data.group_cover_image
            
            if update_data:
                update_data['datetime_updated'] = datetime.now().timestamp()

                update_query = {
                    '$set': update_data
                }

                #update data:
                group_db.get_collection('group').update_many(query, update_query)

            return JSONResponse(content={'status': 'Success'}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Not found'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Bad request'}, status_code=status.HTTP_400_BAD_REQUEST)

#==========================DEPRECATED==============================
#======================UPDATE_GROUP_IMAGE==========================
#==================================================================
@app.post(
    '/update_group_image',
    responses={
        status.HTTP_200_OK: {
            'model': UpdateGroupResponse200
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': UpdateGroupResponse400
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UpdateGroupResponse403
        },
        status.HTTP_404_NOT_FOUND: {
            'model': UpdateGroupResponse404
        }
    },
    description='Update group image',
    tags=['Group'],
    deprecated=True
)
async def update_group_image(
    data: DATA_Update_Group_image,
    data2: dict = Depends(valid_headers)
):
    try:
        # Find a group
        query = {'_id': ObjectId(data.group_id)}
        group = group_db.get_collection('group').find_one(query)
        if group:
            # check owner of group
            if group.get('owner_id') != data2.get('user_id'):
                content = {'status': 'Forbidden'}
                return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

            update_data = {}

            if data.image_type == UpdateGroupImage.AVATAR:
                update_data['group_avatar'] = data.image_url
            elif data.image_type == UpdateGroupImage.COVER:
                update_data['group_cover_image'] = data.image_url
            
            update_data['datetime_updated'] = datetime.now().timestamp()

            update_query = {
                '$set': update_data
            }

            #update data:
            group_db.get_collection('group').update_many(query, update_query)

            return JSONResponse(content={'status': 'Success'}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Not found'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception:
        return JSONResponse(content={'status': 'Bad request'}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#======================INVITE_USERS_TO_GROUP======================
#=================================================================
@app.post(
    '/invite_user_to_group',
    responses={
        status.HTTP_200_OK: {
            'model': AddUserResponse200,
        },
        status.HTTP_403_FORBIDDEN: {
            'model': AddUserResponse403,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AddUserResponse404,
        }
    },
    description='add users to group',
    tags=['Group - Invitation']
)
async def invite_users_to_group(
    data: DATA_Invite_Members,
    data2: dict = Depends(valid_headers),
    # group_id: str = Path(...)
):
    try:
        # Find a group
        query = {'_id': ObjectId(data.group_id)}
        group = group_db.get_collection('group').find_one(query)
        if group:
            # check owner of group or member
            query_member = {
                'group_id': data.group_id,
                'user_id': data2.get('user_id')
            }
            member_group = group_db[GROUP_PARTICIPANT].find_one(query_member)
            if not member_group:
                content = {'status': 'Failed', 'msg': 'User is not the owner or member of group'}
                return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

            logger().info('========add user========')
            logger().info(f'list users: {data.list_user_ids}')

            list_broadcast_user=[]
            for uid in data.list_user_ids:
                invitation_data = GroupInvitation(
                    group_id= data.group_id,
                    inviter_id= data2.get('user_id'),
                    user_id= uid,
                    datetime_created= datetime.now().timestamp()
                )
                logger().info(f'uid: {uid}')
                group_db[GROUP_INVITATION].insert_one(jsonable_encoder(invitation_data))
                list_broadcast_user.append(uid)

            data = {
                'group_name': group.get('group_name'),
                'list_user_ids': list_broadcast_user
            }
            return JSONResponse(content={'status': 'success', 'data': data}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=====================USER_ACCEPT_INVITATION======================
#=================================================================
@app.post(
    '/user_accept_invitation',
    responses={
        status.HTTP_200_OK: {
            'model': AcceptInvitationResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AcceptInvitationResponse404,
        }
    },
    description='user accept invitation',
    tags=['Group - Invitation']
)
async def user_accept_invitation(
    data: DATA_Accept_invitation,
    data2: dict = Depends(valid_headers),
):
    try:
        #find invitation
        query_invitation = {
            '_id': ObjectId(data.invitation_id)
        }
        invitation = group_db[GROUP_INVITATION].find_one(query_invitation)
        if not invitation:
            msg = 'invitation not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        elif invitation.get('user_id') != data2.get('user_id'):
            msg = 'not your invitation'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        # Find a group
        query_group = {'_id': ObjectId(invitation.get('group_id'))}
        group = group_db[GROUP].find_one(query_group)
        if group:
            #add to group participant
            mem_data = GroupMember(
                group_id= invitation.get('group_id'),
                user_id= invitation.get('user_id'),
                inviter_id= invitation.get('inviter_id'),
                datetime_created= datetime.now().timestamp()
            )
            result = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(mem_data)).inserted_id

            # delete invitation
            group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)

            data = {
                'group_id': invitation.get('group_id'),
                'group_name': group.get('group_name'),
                'inviter_id': invitation.get('inviter_id'),
                'participant_id': str(result)
            }

            return JSONResponse(content={'status': 'success', 'data': data}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        msg = str(e)
        return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#======================USER_REJECT_INVITATION=====================
#=================================================================
@app.post(
    '/user_reject_invitation',
    responses={
        status.HTTP_200_OK: {
            'model': AcceptInvitationResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AcceptInvitationResponse404,
        }
    },
    description='user reject invitation',
    tags=['Group - Invitation']
)
async def user_reject_invitation(
    data: DATA_Reject_invitation,
    data2: dict = Depends(valid_headers),
):
    try:
        #find invitation
        query_invitation = {
            '_id': ObjectId(data.invitation_id)
        }
        invitation = group_db[GROUP_INVITATION].find_one(query_invitation,{'group_id':1, 'user_id':1})
        if not invitation:
            msg = 'invitation not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        elif invitation.get('user_id') != data2.get('user_id'):
            msg = 'not your invitation'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
        # delete invitation
        group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#=================================================================
#=====================GROUP_CANCEL_INVITATION=====================
#=================================================================
@app.post(
    '/group_cancel_invitation',
    responses={
        status.HTTP_200_OK: {
            'model': AcceptInvitationResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AcceptInvitationResponse404,
        }
    },
    description='group cancel invitation',
    tags=['Group - Invitation']
)
async def group_cancel_invitation(
    data: DATA_Cancel_invitation,
    data2: dict = Depends(valid_headers),
):
    try:
        #find invitation
        query_invitation = {
            '_id': ObjectId(data.invitation_id),
        }
        invitation = group_db[GROUP_INVITATION].find_one(query_invitation,{'group_id':1, 'user_id':1})
        if not invitation:
            msg = 'invitation not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        
        # check owner of group
        query = {
            'group_id': invitation.get('group_id'),
            'user_id': data2.get('user_id'),
            'is_owner': True
        }
        group_mem = group_db[GROUP_PARTICIPANT].find_one(query)
        if not group_mem:
            msg = 'Error, user is not owner of group!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
        # delete invitation
        group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#===================GROUP_LIST_INVITATION_SENT====================
#=================================================================
@app.get(
    '/group_list_invitation_sent',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='list of invitations sent by the group',
    tags=['Group - Invitation']
)
async def group_list_invitation_sent(
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
                    'localField': 'inviter_id',
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
                    'as': 'inviter_info'
                }
            },
            {
                '$unwind': '$inviter_info'
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
                    'inviter_info': 1,
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
        
        invitation_data = group_db[GROUP_INVITATION].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=invitation_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed','msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=======================USER_LIST_INVITATION======================
#=================================================================
@app.get(
    '/user_list_invitation',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='list of invitations to which the user is invited',
    tags=['Group - Invitation']
)
async def user_list_invitation(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    data2: dict = Depends(valid_headers),
    # user_id: str = Path(..., description='id of user')
):
    try:
        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': {
                    'user_id': data2.get('user_id')
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
                    'localField': 'inviter_id',
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
                    'as': 'inviter_info'
                }
            },
            {
                '$unwind': '$inviter_info'
            },
            {
                '$project': {
                    '_id': 0,
                    'id': {
                        '$toString': '$_id'
                    },
                    'group_info': 1,
                    'inviter_info': 1,
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
        
        invitation_data = group_db[GROUP_INVITATION].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=invitation_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

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
                    'group_id': ObjectId(data.group_id)
                },
                {
                    'user_id': data2.get('user_id')
                }
            ]
        }
        request_join = group_db[GROUP_JOIN_REQUEST].find_one(query_request,{'group_id':1, 'user_id':1})
        if not request_join:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

        #delete request join
        result = group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)

        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#======================NEED_TO_FIX=============================
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
        # find group
        query = {'_id': ObjectId(group_id)}
        group = group_db[GROUP].find_one(query,{'owner_id':1})
        if group:
            #check owner of group
            # if data2.get('user_id') != group.get('owner_id'):
            #     return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

            #get list request
            query_request = {
                'group_id': group_id
            }
            num_skip = (page - 1)*limit
            list_request = group_db[GROUP_JOIN_REQUEST].find(query_request).skip(num_skip).limit(limit)
            result = []
            if list_request.count(True):
                for request_join in list_request:
                    request_join['_id'] = str(request_join['_id'])
                    result.append(request_join)
            
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
        else:
            msg = 'group not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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

#=================================================================
#========================LIST_GROUP_MEMBERS=======================
#=================================================================
@app.get(
    '/list_group_members',
    responses={
        status.HTTP_200_OK: {
            'model': RequestJoinGroupResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': RequestJoinGroupResponse404,
        }
    },
    description='list group members',
    tags=['Group']
)
async def list_group_members(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: str = Query(default=None, description='search text'),
    group_id: str = Query(..., description='id of group'),
    data2: dict = Depends(valid_headers),
):
    try:
        if search:
            query_search = {
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
        else:
            query_search = {}
        
        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': {
                    'group_id': group_id
                }
            },
            {
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'pipeline': [
                        {
                            '$match': query_search
                        },
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
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'inviter_id',
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
                    'as': 'inviter_info'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'user_info': 1,
                    'is_owner': 1,
                    'group_id': 1,
                    'inviter_info': {
                        '$ifNull': [
                            {
                                '$first': '$inviter_info'
                            },
                            None
                        ]
                    },
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
                                'user_info.name': 1
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
        
        members_data = group_db[GROUP_PARTICIPANT].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=members_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=======================REMOVE_GROUP_MEMBERS======================
#=================================================================
@app.post(
    '/remove_members',
    description='Remove group members (only group owner can do it)',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': RemoveMemberResponse404,
        },
        status.HTTP_403_FORBIDDEN: {
            'model': RemoveMemberResponse403,
        },
        status.HTTP_200_OK: {
            'model': RemoveMemberResponse200,
        }
    },
    tags=['Group']
)
async def group_remove_members(
    data: DATA_Remove_Members,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============group_remove_members=================')
    try:
        # check owner of group
        query_mem = {
            'group_id': data.group_id,
            'user_id': data2.get('user_id'),
            'is_owner': True
        }
        mem_data = group_db[GROUP_PARTICIPANT].find_one(query_mem)
        if mem_data:
            #remove member in group_participant
            query_remove_participant = {
                '$and': [
                    {
                        'group_id': data.group_id
                    },
                    {
                        'user_id': {
                            '$in': data.list_user_ids
                        }
                    }
                ]
            }
            group_db[GROUP_PARTICIPANT].delete_many(query_remove_participant)

            #broadcast to list user(notification)
            #############################################
            #############################################
            #############################################
            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
        else:
            msg = 'Error, user is not owner of group!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#==========================NEED_TO_FIX============================
#==========================DELETE_GROUP===========================
#=================================================================
@app.delete(
    '/delete_group',
    description='delete group',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': DeleteGroupResponse404
        },
        status.HTTP_403_FORBIDDEN: {
            'model': DeleteGroupResponse403
        },
        status.HTTP_200_OK: {
            'model': DeleteGroupResponse200
        }
    },
    tags=['Group'],
    deprecated=True
)
async def remove_group(
    data: DATA_Delete_Group,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============remove_group=================')
    # Find a group
    query = {'_id': ObjectId(data.group_id)}
    group = group_db.get_collection('group').find_one(query)
    if group:
        # check owner of group
        if group.get('owner_id') != data2.get('user_id'):
            content = {'status': 'Failed', 'msg': 'User is not the owner of group'}
            return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)
        
        query_participant = {
            'group_id': data.group_id
        }

        logger().info('get list user_id of group_members')
        # get list user_id of group_members
        group_members = group_db['group_participant'].find(query_participant)
        logger().info(f'group_members: {group_members}')
        list_group_members = []
        for mem in group_members:
            list_group_members.append(mem.get('user_id'))
        logger().info(f'list_group_members: {list_group_members}')

        #broadcast to list user(notification)
        #############################################
        #############################################
        #############################################
        
        # remove group_participant
        group_db.get_collection('group_participant').delete_many(query_participant)

        # request remove group chat
        #######################################################
        #######################################################
        #######################################################

        # remove group in DB
        group_db.get_collection('group').find_one_and_delete(query)

        #request remove list user out of group chat
        #################################################
        #################################################
        #################################################
            
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#==========================NEED_TO_FIX============================
#=========================GET_GROUP_INFO==========================
#=================================================================
@app.get(
    '/group_info/{group_id}',
    description='get group infomation',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': CreateGroupResponse200
        },
        status.HTTP_200_OK: {
            'model': CreateGroupResponse200
        }
    },
    tags=['Group']
)
async def get_group_info(
    group_id: str = Path(..., description='ID of the group'),
    data2: dict = Depends(valid_headers),
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        group_info = get_one_group_info(group_id)
        if group_info:
            query = {
                '$and': [
                    {
                        'group_id': group_id
                    },
                    {
                        'user_id': data2.get('user_id')
                    }
                ] 
            }
            invitation = group_db[GROUP_INVITATION].find_one(query)
            participant = group_db[GROUP_PARTICIPANT].find_one(query)
            request_join = group_db[GROUP_JOIN_REQUEST].find_one(query)

            group_info['is_owner'] = (data2.get('user_id') == group_info.get('owner_id'))
            group_info['is_member'] = True if participant else False
            group_info['is_invited'] = True if invitation else False
            group_info['is_requested'] = True if request_join else False

            return JSONResponse(content={'status': 'success', 'data': group_info}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found'
            return JSONResponse(content={'status': 'Not Found!', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Bad Requests!'}, status_code=status.HTTP_400_BAD_REQUEST)

#=======================DEPRECATED============================
#=====================LIST_ALL_GROUP_CREATED======================
#=================================================================
@app.get(
    '/all_group_created',
    description='list all group created',
    # responses={
    #     status.HTTP_400_BAD_REQUEST: {
    #         'model': AllGroupResponse400
    #     },
    #     status.HTTP_200_OK: {
    #         'model': AllGroupResponse200
    #     }
    # },
    tags=['Group'],
    deprecated=True
)
async def list_all_groups_created(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    data2: dict = Depends(valid_headers),
    # user_id: str = Path(..., description='ID of user')
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        # if search:
        #     query = {
        #         '$and': [
        #             {
        #                 'owner_id': user_id
        #             },
        #             {
        #                 '$text': {
        #                     '$search': search
        #                 }
        #             }
        #         ]
        #     }
        # else:
        #     query = {
        #                 'owner_id': user_id
        #             }
        
        filter = []
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter.append(query_search)

        query_owner = {
            'owner_id': data2.get('user_id')
        }
        filter.append(query_owner)
        
        query_status = {
            'group_status': GroupStatus.ENABLE
        }
        filter.append(query_status) 

        if filter:
            query_filter = {
                '$and': filter
            }
        else:
            query_filter = {}

        num_skip = (page - 1)*limit
        all_group = group_db.get_collection(GROUP).find(query_filter).skip(num_skip).limit(limit)
        all_group_info = []
        if all_group.count(True):
            for group in all_group:
                group['_id'] = str(group['_id'])
                query_participant = {
                    'group_id': group['_id']
                }
                group_members_count = group_db[GROUP_PARTICIPANT].find(query_participant).count()
                group['num_members'] = group_members_count + 1
                all_group_info.append(group)

        num_group = group_db.get_collection(GROUP).find(query_filter).count()
        logger().info(f'num group: {num_group}')
        num_pages = ceil(num_group/limit)

        meta_data = {
            'count': all_group.count(True),
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }
        
        return JSONResponse(content={'status': 'success', 'data': all_group_info, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Bad Requests!'}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=====================LIST_ALL_GROUP_DISCOVER=====================
#=================================================================
@app.get(
    '/all_group_discover',
    description='list all group discover',
    # responses={
    #     status.HTTP_400_BAD_REQUEST: {
    #         'model': AllGroupResponse400
    #     },
    #     status.HTTP_200_OK: {
    #         'model': AllGroupResponse200
    #     }
    # },
    tags=['Group']
)
async def list_all_groups_discover(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    # user_id: str = Path(..., description='ID of user'),
    group_type: str = Query(default=None, description='filter by group type'),
    # group_datetime_created: float = Query(default=None, description='filter by group datetime created'),
    data2: dict = Depends(valid_headers),
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        filter = []
        if search:
            query_search = {
                'group_name': {
                    '$regex': search,
                    '$options': 'i',
                }
            }
            filter.append(query_search)

        
        query_status = {
            'group_status': GroupStatus.ENABLE,
            'is_deleted': False
        }
        filter.append(query_status)  

        if group_type:
            query_type = {
                'group_type': group_type
            }
            filter.append(query_type)

        # if group_datetime_created:
        #     query_datetime_created = {
        #         'datetime_created': {
        #             '$gt': group_datetime_created,
        #             '$lt': group_datetime_created + 86400
        #         }
        #     }
        #     filter.append(query_datetime_created)

        if filter:
            query_filter = {
                '$and': filter
            }
        else:
            query_filter = {}

        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': query_filter
            },
            {
                '$set': {
                    '_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'group_participant',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        { '$eq': ['$user_id', data2.get('user_id')] },
                                        { '$eq': ['$group_id', '$$id']}
                                    ]
                                }
                            }
                        },
                        {
                            '$set': {
                                '_id': {'$toString': '$_id'},
                            }
                        }
                    ],
                    'as': 'members_participant'
                }
            },
            {
                '$set': {
                    'is_member': {
                        '$ne': ['$members_participant', []]
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'group_invitation',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        { '$eq': ['$user_id', data2.get('user_id')] },
                                        { '$eq': ['$group_id', '$$id']}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'invitation'
                }
            },
            {
                '$set': {
                    'is_invited': {
                        '$ne': ['$invitation', []]
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'group_join_request',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        { '$eq': ['$user_id', data2.get('user_id')] },
                                        { '$eq': ['$group_id', '$$id']}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'request_join'
                }
            },
            {
                '$set': {
                    'is_requested': {
                        '$ne': ['$request_join', []]
                    }
                }
            },
            {
                '$match': {
                    'is_member': False
                }
            },
            {
                '$lookup': {
                    'from': 'group_participant',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$group_id', '$$id']
                                }
                            }
                        },
                        {
                            '$set': {
                                '_id': {'$toString': '$_id'},
                            }
                        }
                    ],
                    'as':'member_in_group'
                }
            },
            {
                '$set': {
                    'member_count': {
                        '$size': '$member_in_group'
                    } 
                }
            },
            {
                '$project': {
                    'member_in_group': 0,
                    'owner_id': 0,
                    'group_status': 0,
                    'members_participant': 0,
                    'invitation': 0,
                    'request_join': 0,
                    'is_approved': 0,
                    'is_deleted': 0
                }
            },
            {
                '$facet': {
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
                                'group_name': 1
                            }
                        },
                        { 
                            '$skip': num_skip
                        },
                        { 
                            '$limit': limit 
                        }
                    ]
                }
            },
            {
                '$unwind': '$metadata'         
            }
        ]
        group_data = group_db[GROUP].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=group_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Bad Requests!', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#=================================================================
#=======================LIST_ALL_GROUP_JOINED=====================
#=================================================================
@app.get(
    '/all_group_joined',
    description='list all group joined',
    # responses={
    #     status.HTTP_400_BAD_REQUEST: {
    #         'model': AllGroupResponse400
    #     },
    #     status.HTTP_200_OK: {
    #         'model': AllGroupResponse200
    #     }
    # },
    tags=['Group']
)
async def list_all_groups_joined(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    group_type: str = Query(default=None, description='filter by group type'),
    data2: dict = Depends(valid_headers),
    # user_id: str = Path(..., description='ID of user')
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        filter = []
        if search:
            query_search = {
                'group_name': {
                    '$regex': search,
                    '$options': 'i',
                }
            }
            filter.append(query_search)

        
        query_status = {
            'group_status': GroupStatus.ENABLE,
            'is_deleted': False
        }
        filter.append(query_status)  

        if group_type:
            query_type = {
                'group_type': group_type
            }
            filter.append(query_type)

        # if group_datetime_created:
        #     query_datetime_created = {
        #         'datetime_created': {
        #             '$gt': group_datetime_created,
        #             '$lt': group_datetime_created + 86400
        #         }
        #     }
        #     filter.append(query_datetime_created)

        if filter:
            query_filter = {
                '$and': filter
            }
        else:
            query_filter = {}

        num_skip = (page - 1)*limit
        pipeline = [
            {
                '$match': query_filter
            },
            {
                '$set': {
                    '_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'group_participant',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        { '$eq': ['$user_id', data2.get('user_id')] },
                                        { '$eq': ['$group_id', '$$id']}
                                    ]
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'is_owner': 1
                            }
                        }
                    ],
                    'as': 'members_participant'
                }
            },
            {
                '$unwind': '$members_participant'
            },
            {
                '$set': {
                    'is_owner': '$members_participant.is_owner'
                }
            },
            {
                '$lookup': {
                    'from': 'group_participant',
                    'let': {
                        'id': '$_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$group_id', '$$id']
                                }
                            }
                        },
                        {
                            '$set': {
                                '_id': {'$toString': '$_id'},
                            }
                        }
                    ],
                    'as':'member_in_group'
                }
            },
            {
                '$set': {
                    'member_count': {
                        '$size': '$member_in_group'
                    } 
                }
            },
            {
                '$project': {
                    'member_in_group': 0,
                    'owner_id': 0,
                    'group_status': 0,
                    'members_participant': 0,
                    'invitation': 0,
                    'request_join': 0,
                    'is_approved': 0,
                    'is_deleted': 0
                }
            },
            {
                '$facet': {
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
                                'group_name': 1
                            }
                        },
                        { 
                            '$skip': num_skip
                        },
                        { 
                            '$limit': limit 
                        }
                    ]
                }
            },
            {
                '$unwind': '$metadata'         
            }
        ]
        group_data = group_db[GROUP].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=group_data, page=page)
        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Bad Requests!', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
