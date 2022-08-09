#  Copyright (c) 2021.
from datetime import datetime
from enum import unique
from importlib.metadata import metadata
from json import JSONEncoder
from math import ceil
from typing import List, Optional, Union
from app.utils.question_utils.question import get_data_and_metadata
from models.db.group import Group_DB, GroupMember

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

#==================================================================
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
            if (group.get('owner_id') != data2.get('user_id')) and not member_group:
                content = {'status': 'Failed', 'msg': 'User is not the owner or member of group'}
                return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

            logger().info('========add user========')
            logger().info(f'list users: {data.list_user_ids}')

            list_broadcast_user=[]
            for uid in data.list_user_ids:
                logger().info(uid)
                json_data = {
                    'group_id': data.group_id,
                    'inviter_id': data2.get('user_id'),
                    'user_id': uid,
                    'datetime_created': datetime.now().timestamp()
                }
                logger().info(uid)
                try:
                    group_db[GROUP_INVITATION].insert_one(json_data)
                    list_broadcast_user.append(uid)
                except Exception as e:
                    logger().error(e)
            data = {
                'group_name': group.get('group_name')
            }
            return JSONResponse(content={'status': 'success', 'data': data, 'list_ids': list_broadcast_user}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#=================================================================
#=========================ACCEPT_INVITATION=======================
#=================================================================
@app.post(
    '/accept_invitation',
    responses={
        status.HTTP_200_OK: {
            'model': AcceptInvitationResponse200,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AcceptInvitationResponse404,
        }
    },
    description='accept invitation',
    tags=['Group - Invitation']
)
async def accept_invitation(
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
            json_data = {
                'group_id': invitation.get('group_id'),
                'user_id': data2.get('user_id'),
                'datetime_created': datetime.now().timestamp()
            }
            result = group_db[GROUP_PARTICIPANT].insert_one(json_data).inserted_id

            # delete invitation
            group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)

            data = {
                'group_id': invitation.get('group_id'),
                'group_name': group.get('group_name'),
                'owner_id': group.get('owner_id'),
                'inviter_id': invitation.get('inviter_id'),
                'group_chat_id': group.get('group_chat_id'),
                'participant_id': str(result)
            }

            return JSONResponse(content={'status': 'success', 'data': data}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        msg = str(e)
        return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

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
            '_id': ObjectId(data.invitation_id)
        }
        invitation = group_db[GROUP_INVITATION].find_one(query_invitation,{'group_id':1, 'user_id':1})
        if not invitation:
            msg = 'invitation not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        
        # Find a group
        query = {'_id': ObjectId(invitation.get('group_id'))}
        group = group_db[GROUP].find_one(query,{'owner_id': 1})
        logger().info(f'group: {group}')
        if group:
            #check owner of group
            if data2.get('user_id') != group.get('owner_id'):
                msg = 'not owner of group'
                return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        else:
            #delete invitation
            group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)
            
            msg = 'group not found'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        
        # delete invitation
        group_db[GROUP_INVITATION].find_one_and_delete(query_invitation)
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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
        # find group
        query = {'_id': ObjectId(group_id)}
        group = group_db[GROUP].find_one(query,{'owner_id':1})
        if group:
            #check owner of group
            if data2.get('user_id') != group.get('owner_id'):
                return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

            #get list request
            query_invitation = {
                'group_id': group_id
            }
            num_skip = (page - 1)*limit
            list_invitation = group_db[GROUP_INVITATION].find(query_invitation).skip(num_skip).limit(limit)
            result = []
            if list_invitation.count(True):
                for invitation in list_invitation:
                    invitation['_id'] = str(invitation['_id'])
                    result.append(invitation)

            num_invitation = group_db[GROUP_INVITATION].find(query).count()
            logger().info(f'num invitation: {num_invitation}')
            num_pages = ceil(num_invitation/limit)

            meta_data = {
                'count': list_invitation.count(True),
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
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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
            json_data = {
                'group_id': request_join.get('group_id'),
                'user_id': request_join.get('user_id'),
                'datetime_created': datetime.now().timestamp()
            }
            request_id = group_db[GROUP_PARTICIPANT].insert_one(json_data).inserted_id

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
        # find group
        query = {'_id': ObjectId(group_id)}
        group = group_db[GROUP].find_one(query,{'owner_id':1})
        if group:
            #check owner of group
            if data2.get('user_id') != group.get('owner_id'):
                return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)

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

#=================================================================
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
    group_id: str = Query(..., description='id of group'),
    data2: dict = Depends(valid_headers),
):
    try:
        # find group
        
        query = {'_id': ObjectId(group_id)}
        group = group_db[GROUP].find_one(query,{'owner_id':1})
        if group:
            del group['_id']
            query_group_participant = {
                'group_id': group_id
            }
            list_members = list(group_db[GROUP_PARTICIPANT].find(query_group_participant))
            import functools
            result = functools.reduce(lambda a, b: a + [b['user_id']],list_members,[])

            group['members'] = result

            return JSONResponse(content={'status': 'success', 'data': group}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

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
        # Find a group
        query = {'_id': ObjectId(data.group_id)}
        group = group_db.get_collection('group').find_one(query)
        if group:
            # check owner of group
            if group.get('owner_id') != data2.get('user_id'):
                content = {'status': 'Failed', 'msg': 'User is not the owner of group'}
                return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)
            
            logger().info('========add user========')
            logger().info(f'========list user: {data.list_user_ids}========')

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

            #request remove list user out of group chat
            #################################################
            #################################################
            #################################################
                
            #broadcast to list user(notification)
            #############################################
            #############################################
            #############################################
            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#=================================================================
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
    tags=['Group']
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

#=================================================================
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

#=================================================================
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
    tags=['Group']
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
    group_datetime_created: float = Query(default=None, description='filter by group datetime created'),
    data2: dict = Depends(valid_headers),
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        # query = {
        #     '$and': [
        #         {
        #             'owner_id': {
        #                 '$ne': user_id
        #             }
        #         },
        #         {
        #             'members': {
        #                 '$ne': user_id
        #             }
        #         }
        #     ]
        # }
        # if search:
        #     query_group = {
        #                 '$text': {
        #                     '$search': search
        #                 }
        #             }
        # else:
        #     query_group = {}

        filter = []
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter.append(query_search)
        
        query_status = {
            'group_status': GroupStatus.ENABLE
        }
        filter.append(query_status)  

        if group_type:
            query_type = {
                'group_type': group_type
            }
            filter.append(query_type)

        if group_datetime_created:
            query_datetime_created = {
                'datetime_created': {
                    '$gt': group_datetime_created,
                    '$lt': group_datetime_created + 86400
                }
            }
            filter.append(query_datetime_created)

        if filter:
            query_filter = {
                '$and': filter
            }
        else:
            query_filter = {}

        num_skip = (page - 1)*limit
        all_group = group_db.get_collection(GROUP).find(query_filter).skip(num_skip).limit(limit)
        all_group_info = []
        logger().info(f'all group count: {all_group.count()}')
        if all_group.count(True):
            for group in all_group:
                group['_id'] = str(group['_id'])
                query_participant = {
                    'group_id': group['_id']
                }
                group_members_count = group_db[GROUP_PARTICIPANT].find(query_participant).count()
                group['num_members'] = group_members_count + 1
                
                query = {
                    '$and': [
                        {
                            'group_id': group['_id']
                        },
                        {
                            'user_id': data2.get('user_id')
                        }
                    ] 
                }
                invitation = group_db[GROUP_INVITATION].find_one(query)
                participant = group_db[GROUP_PARTICIPANT].find_one(query)
                request_join = group_db[GROUP_JOIN_REQUEST].find_one(query)

                group['is_owner'] = (data2.get('user_id') == group.get('owner_id'))
                group['is_member'] = True if participant else False
                group['is_invited'] = True if invitation else False
                group['is_requested'] = True if request_join else False
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
    data2: dict = Depends(valid_headers),
    # user_id: str = Path(..., description='ID of user')
):
    logger().info('===============get_group_info=================')
    # Find a group
    try:
        query_group_participant = {
            'user_id': data2.get('user_id')
        }
        list_group_participant = list(group_db[GROUP_PARTICIPANT].find(query_group_participant,{'group_id': 1}))
        import functools
        all_group_join = functools.reduce(lambda a, b: a + [ObjectId(b['group_id'])],list_group_participant,[])
        
        filter = []
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter.append(query_search)

        query_group = {
            '_id': {
                '$in': all_group_join
            }
        }
        filter.append(query_group)
        
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
