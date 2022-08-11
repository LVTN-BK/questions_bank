from datetime import datetime
from app.utils.question_utils.question import get_data_and_metadata
from models.db.group import Group_DB, GroupInvitation, GroupMember
from bson import ObjectId
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse

from configs import GROUP, GROUP_INVITATION, GROUP_JOIN_REQUEST, GROUP_PARTICIPANT, app, group_db
from models.request.group import DATA_Accept_invitation, DATA_Cancel_invitation, DATA_Invite_Members, DATA_Reject_invitation
# import response models
from models.response import *

# Config logging
from configs.logger import logger
from fastapi.encoders import jsonable_encoder
from app.utils._header import valid_headers


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
