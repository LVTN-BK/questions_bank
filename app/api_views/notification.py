#  Copyright (c) 2021.
from datetime import datetime
from math import ceil
from typing import List, Optional, Union

import pymongo
import requests
from bson import ObjectId
from fastapi import Path, Query, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from app.utils.check_noti_setting import get_list_user_id_enable_noti_type
from app.utils.notification_content import get_notification_content

from configs import GROUP_PROVIDER_API, NOTI_COLLECTION, NOTI_SETTING_COLLECTION, app, noti_db, LIST_PROVIDER_API
from models.request.notification import DATA_Create_Noti_Group_Members_Except_User, DATA_Create_Noti_List_User
# import response models
from models.response import *
from models.system_and_feeds.notification import NotificationContentManage, NotificationTypeManage

from . import notification_manage
# Config logging
from configs.logger import logger
from fastapi import WebSocket, Form
from starlette.websockets import WebSocketDisconnect

#==================================================================
#=====================SYSTEM_ESTABLISH_CONNECTION==================
#==================================================================
@app.websocket('/ws/notification/sys/{user_id}')
async def noti_sys_establish_connection(
        websocket: WebSocket, user_id: Union[int, str]
        # token: str = Query(..., description='Token for authenticate from main service')
):
    try:
        token='111'
        # Accept the connection
        connect = await notification_manage.connect(websocket=websocket,user_id=user_id,token=token)
        logger().info(f'system connection: {notification_manage.connections}')
        # Always listen for receiving data from client
        if connect:
            try:
                while True:
                    json_data = await websocket.receive_json()
                    await websocket.send_json({
                        'json_data': json_data
                    })
            except WebSocketDisconnect:
                try:
                    # Remove connection out of active connection list
                    notification_manage.remove_active_member(user_id=user_id,websocket=websocket)
                    logger().info(f'system connection after remove: {notification_manage.connections}')
                except KeyError:
                    logger().warning(f'{user_id} not exist in SYS_ACTIVE_CONNECTION')
    except Exception as e:
        logger().error(e.args)

#=================================================================
#=========================GET_ALL_NOTIFICATION====================
#=================================================================
@app.get(
    '/notification/{user_id}/all',
    responses={
        status.HTTP_200_OK: {
            'model': AllNotificationResponse200,
            'description': 'All notification was retrieved successfully'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': AllNotificationResponse404,
            'description': 'Failed!'
        }
    },
    description='get all notification of user',
    tags=['Notification']
)
async def all_notifications(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    user_id: str = Query(..., description='ID of user')
):
    # Find all noti
    query = {
        'receive_ids': {
            '$elemMatch':{
                '$eq': user_id
            }
        }
    }

    try:
        num_skip = (page - 1)*limit
        all_noti = []
        noti = noti_db[NOTI_COLLECTION].find(query, {'sender_id': 1, 'noti_type': 1, 'target': 1, 'content': 1, 'seen_ids': 1,'datetime_created': 1}).sort('datetime_created', -1).skip(num_skip).limit(limit)

        logger().info(noti.count(True))
        if noti.count(True):
            for ele in noti:
                ele['_id'] = str(ele['_id'])
                ele['is_read'] = (user_id in ele['seen_ids'])
                del ele['seen_ids']
                all_noti.append(ele)
        num_noti = noti_db[NOTI_COLLECTION].find(query).count()
        num_pages = ceil(num_noti/limit)

        logger().info(noti.count(True))
        meta_data = {
            'count': noti.count(True),
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }

        return JSONResponse(content={'status': 'success', 'data': all_noti, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().info(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)

#=================================================================
#===========CREATE_NOTIFICATION_TO_GROUP_MEMBERS_EXCEPT_USER======
#=================================================================
@app.post(
    '/create_group_noti_except_user/{group_id}',
    description='create notification to group members',
    responses={
        status.HTTP_200_OK: {
            'model': CreateNotificationGroupResponse200,
            'description': 'When notification successfully created!'
        }
    },
    tags=['Notification']
)
async def create_notification_to_group_members_except_user(
    data: DATA_Create_Noti_Group_Members_Except_User
):
    logger().info('===============create_notification=================')
    try:
        # insert to DB
        receive_ids = await notification_manage.get_group_members_id_except_user(group_id=data.group_id, user_id=data.user_id, noti_type=data.noti_type)
        
        #get notification content
        content = get_notification_content(noti_type=data.noti_type)

        json_data = {
            'sender_id': data.user_id,
            'receive_ids': receive_ids,
            'seen_ids': [],
            'noti_type': data.noti_type,
            'content': content,
            'target': jsonable_encoder(data.target),
            'datetime_created': datetime.now().timestamp()
        }
        _id = noti_db[NOTI_COLLECTION].insert_one(json_data).inserted_id

        json_data['_id'] = str(json_data['_id'])
        del json_data['receive_ids']
        del json_data['seen_ids']

        # Broastcast to active members:
        await notification_manage.broadcast_notification_to_list_specific_user(receive_ids=receive_ids, json_data=json_data)

        return JSONResponse(content={'status': 'success', 'noti_id': str(_id)}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = str(e)
        return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#=================================================================
#==================CREATE_NOTIFICATION_TO_LIST_USER===============
#=================================================================
@app.post(
    '/notification/list_users/create',
    description='create notification to list specific user',
    responses={
        status.HTTP_200_OK: {
            'model': CreateNotificationListUserResponse200,
            'description': 'When notification successfully created!'
        }
    },
    tags=['Notification']
)
async def create_notification_to_list_specific_user(
        data: DATA_Create_Noti_List_User
): 
    logger().info('===============send_notification_to_list_specific_user=================')
    # filter user_id enable notification with noti_type
    get_list_user_id_enable_noti_type(list_users=data.list_users, noti_type=data.noti_type)

    #get notification content
    content = get_notification_content(noti_type=data.noti_type)
    
    
    # insert to DB
    json_data = {
        'sender_id': data.sender_id,
        'receive_ids': data.list_users,
        'noti_type': data.noti_type,
        'content': content,
        'target': jsonable_encoder(data.target),
        'seen_ids': [],
        'datetime_created': datetime.now().timestamp()
    }
    _id = noti_db['notification'].insert_one(json_data).inserted_id

    json_data['_id'] = str(json_data['_id'])
    del json_data['receive_ids']
    del json_data['seen_ids']

    # Broastcast to active user:
    await notification_manage.broadcast_notification_to_list_specific_user(receive_ids=data.list_users, json_data=json_data)

    return JSONResponse(content={'status': 'success', 'noti_id': str(_id)}, status_code=status.HTTP_200_OK)

#=================================================================
#======================DELETE_NOTIFICATION========================
#=================================================================
@app.delete(
    '/notification/{user_id}/delete',
    description='Remove a notification',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': DeleteNotificationResponse400
        },
        status.HTTP_200_OK: {
            'model': DeleteNotificationResponse200
        }
    },
    tags=['Notification']
)
async def remove_notification(
        user_id: Union[int, str] = Path(..., description='ID of user'),
        noti_id: str = Query(..., description='ID of notification will be deleted by user'),
):
    try:
        query = {
            '_id': {
                '$eq': ObjectId(noti_id)
            }
        }
        update = {
            '$pull': {
                'receive_ids': {
                    '$in': [user_id]
                }
            }
        }
        noti_db['notification'].update_many(query, update)
        
        return JSONResponse(content={'status': 'Deleted!'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().info(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)
    

#=================================================================
#=================MARK_NOTIFICATION_AS_SEEN(READ)=================
#=================================================================
@app.post(
    '/notification/{user_id}/read',
    responses={
        status.HTTP_200_OK: {
            'model': MarkNotificationAsSeenResponse200
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': MarkNotificationAsSeenResponse400
        }
    },
    description='Mark notification as seen',
    tags=['Notification']
)
async def mark_notification_as_seen(
        user_id: str = Path(..., description='ID of user'),
        noti_id: Optional[str] = Form(default=None, description="ID of notification/mark as read all if noti_id is None")
):
    logger().info(f'==========mark_notification_as_seen============')
    try:
        logger().info(f'noti_id: {noti_id}')
        logger().info(f'user_id: {user_id}')
        if noti_id:
            query = {
                '$and': [
                    {
                        '_id': {
                            '$eq': ObjectId(noti_id)
                        }
                    },
                    {
                        'receive_ids': {
                            '$elemMatch': {
                                '$eq': user_id
                            }
                        }
                    },
                    {
                        'seen_ids': {
                            '$ne': user_id
                        }
                    }
                ]
                    
            }
            update = {
                '$addToSet': {
                    'seen_ids': user_id
                }
            }
            # mark as seen
            noti_db['notification'].update_one(query, update)
        else:
            query = {
                '$and': [
                    {
                        'receive_ids': {
                            '$elemMatch': {
                                '$eq': user_id
                            }
                        }
                    },
                    {
                        
                        'seen_ids': {
                            '$ne': user_id
                        }
                        
                    }
                ]
                        
            }
            update = {
                '$addToSet': {
                    'seen_ids': user_id
                }
            }

            # mark as seen
            noti_db['notification'].update_many(query, update)

        return JSONResponse(content={'status': 'successful!'}, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger().info(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_400_BAD_REQUEST)
        

#=================================================================
#======================ALL_UNREAD_NOTIFICATION====================
#=================================================================
@app.get(
    '/notification/{user_id}/unread',
    responses={
        status.HTTP_200_OK: {
            'model': UnreadNotificationResponse200
        },
        status.HTTP_404_NOT_FOUND: {
            'model': UnreadNotificationResponse404
        }
    },
    description='get all unread notification',
    tags=['Notification']
)
async def unread_message(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    user_id: str = Path(..., description='ID of user')
):
    # Find all noti unread
    logger().info('===========unread_message==========')
    query = {
        '$and': [
            {
                'receive_ids': {
                    '$elemMatch':{
                        '$eq': user_id
                    }
                }
            },
            {
                'seen_ids': {
                    '$ne': user_id
                }
            }
        ]
    }

    try:
        num_skip = (page - 1)*limit
        noti = noti_db[NOTI_COLLECTION].find(query,{'sender_id': 1, 'content': 1, 'target': 1, 'noti_type': 1, 'datetime_created': 1}).sort([('datetime_created', -1)]).skip(num_skip).limit(limit)
        all_noti = []
        logger().info('bbbbbbbbbbbbb')
        if noti.count(True):
            for ele in noti:
                ele['_id'] = str(ele['_id'])
                all_noti.append(ele)
        
        num_noti = noti_db[NOTI_COLLECTION].find(query).count()
        num_pages = ceil(num_noti/limit)

        meta_data = {
            'count': noti.count(True),
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }
        return JSONResponse(content={'status': 'success', 'data': all_noti, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().info(e)
        return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_404_NOT_FOUND)


#=================================================================
#======================INITIAL_NOTIFICATION_SETTING===============
#=================================================================
@app.post(
    '/initial_notification_setting',
    description='init notification setting',
    responses={
        status.HTTP_200_OK: {
            'model': InitNotificationSetting200,
            'description': 'When notification successfully created!'
        }
    },
    tags=['Notification']
)
async def initial_notification_setting_to_user(
        user_id: str = Query(..., description="User ID who create the notification")
):
    logger().info('===============initial_notification_setting=================')
    # insert to DB Notification Type Comment
    noti_db[NOTI_SETTING_COLLECTION].update_one(
        {
            'user_id': user_id,
            'noti_type': NotificationTypeManage.COMMENT
        },
        {
            '$set': {
                'is_enable': True
            }
        },
        upsert=True
    )
    
    # insert to DB Notification Type Follow
    noti_db[NOTI_SETTING_COLLECTION].update_one(
        {
            'user_id': user_id,
            'noti_type': NotificationTypeManage.FOLLOW
        },
        {
            '$set': {
                'is_enable': True
            }
        },
        upsert=True
    )
    
    # insert to DB Notification Type Unfollow
    noti_db[NOTI_SETTING_COLLECTION].update_one(
        {
            'user_id': user_id,
            'noti_type': NotificationTypeManage.UNFOLLOW
        },
        {
            '$set': {
                'is_enable': True
            }
        },
        upsert=True
    )
    
    # insert to DB Notification Type Share
    noti_db[NOTI_SETTING_COLLECTION].update_one(
        {
            'user_id': user_id,
            'noti_type': NotificationTypeManage.SHARE
        },
        {
            '$set': {
                'is_enable': True
            }
        },
        upsert=True
    )

    return JSONResponse(content={'status': 'success', 'user_id': user_id}, status_code=status.HTTP_200_OK)


#=================================================================
#======================UPDATE_NOTIFICATION_SETTING================
#=================================================================
@app.post(
    '/update_notification_setting',
    description='update notification setting',
    responses={
        status.HTTP_200_OK: {
            'model': UpdateNotificationSetting200,
            'description': 'When notification successfully created!'
        }
    },
    tags=['Notification']
)
async def update_notification_setting(
        user_id: str = Form(..., description="User ID who create the notification"),
        noti_type: str = Form(..., description="type of notification"),
        is_enable: bool = Form(..., description='setting status')
):
    logger().info('===============initial_notification_setting=================')
    # insert to DB Notification Type Comment
    noti_db[NOTI_SETTING_COLLECTION].update_one(
        {
            'user_id': user_id,
            'noti_type': noti_type
        },
        {
            '$set': {
                'is_enable': is_enable
            }
        },
        upsert=True
    )
    
    return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
