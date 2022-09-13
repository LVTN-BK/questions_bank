#  Copyright (c) 2021.
from datetime import datetime
from math import ceil
from typing import List, Optional, Union
from app.utils._header import valid_headers
from bson import ObjectId
from fastapi import Path, Query, Body, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from app.utils.notification_utils.check_noti_setting import get_list_user_id_enable_noti_type
from app.utils.group_utils.group import get_group_members_id_except_user
from app.utils.notification_utils.notification_content import get_notification_content
from app.utils.question_utils.question import get_data_and_metadata

from configs import NOTI_COLLECTION, NOTI_SETTING_COLLECTION, app, noti_db
from models.request.notification import DATA_Create_Noti_Group_Members_Except_User, DATA_Create_Noti_List_User, DATA_Delete_Notification, DATA_Mark_Notification_As_Seen, DATA_Update_Notification_Setting
# import response models
from models.response import *
from models.define.notification import NotificationContentManage, NotificationTypeManage

from .. import notification_manage
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
        # token='111'
        # Accept the connection
        connect = await notification_manage.connect(websocket=websocket,user_id=user_id)
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
    '/user_all_notification',
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
async def user_all_notification(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit
        pipeline=[
            {
                '$match': {
                    '$and': [
                        {
                            '$expr': {
                                '$in': [data2.get('user_id'), '$receiver_ids']
                            }
                        },
                        {
                            'removed_ids': {
                                '$not': {
                                    '$elemMatch': {
                                        '$eq': data2.get('user_id')
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'sender_id',
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
                    'as': 'sender_data'
                }
            },
            {
                '$set': {
                    'sender_info': {
                        '$ifNull': [{'$first': '$sender_data'}, None]
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
                                'sender_info': 1,
                                'is_read': {
                                    '$in': [data2.get('user_id'), '$seen_ids']
                                },
                                "noti_type": 1,
                                "content": 1,
                                'target': 1,
                                'datetime_created': 1
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

        list_notification = noti_db[NOTI_COLLECTION].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=list_notification, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().info(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#===========================DEPRECATED============================
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
    tags=['Notification'],
    deprecated=True
)
async def create_notification_to_group_members_except_user(
    data: DATA_Create_Noti_Group_Members_Except_User
):
    logger().info('===============create_notification=================')
    try:
        # insert to DB
        receive_ids = get_group_members_id_except_user(group_id=data.group_id, user_id=data.user_id)
        
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


#==========================DEPRECATED=============================
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
    tags=['Notification'],
    deprecated=True
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
        'receiver_ids': data.list_users,
        'noti_type': data.noti_type,
        'content': content,
        'target': jsonable_encoder(data.target),
        'seen_ids': [],
        'datetime_created': datetime.now().timestamp()
    }
    _id = noti_db['notification'].insert_one(json_data).inserted_id

    json_data['_id'] = str(json_data['_id'])
    del json_data['receiver_ids']
    del json_data['seen_ids']

    # Broastcast to active user:
    notification_manage.broadcast_notification_to_list_specific_user(receive_ids=data.list_users, json_data=json_data)

    return JSONResponse(content={'status': 'success', 'noti_id': str(_id)}, status_code=status.HTTP_200_OK)


#=================================================================
#======================DELETE_NOTIFICATION========================
#=================================================================
@app.delete(
    '/delete_notification',
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
async def delete_notification(
    data: DATA_Delete_Notification,
    data2: dict = Depends(valid_headers)
):
    try:
        query = {
            '_id': {
                '$eq': ObjectId(data.noti_id)
            },
            'receiver_ids': {
                '$elemMatch': {
                    '$eq': data2.get('user_id')
                }
            }
                        
        }
        update = {
            '$addToSet': {
                'removed_ids': data2.get('user_id')
            }
        }
        noti_db[NOTI_COLLECTION].find_one_and_update(query, update)
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    

#=================================================================
#=================MARK_NOTIFICATION_AS_SEEN(READ)=================
#=================================================================
@app.put(
    '/mark_notification_as_seen',
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
    data: DATA_Mark_Notification_As_Seen,
    data2: dict = Depends(valid_headers)
):
    logger().info(f'==========mark_notification_as_seen============')
    try:
        logger().info(f'noti_id: {data.noti_id}')
        if data.noti_id:
            query = {
                '$and': [
                    {
                        '_id': {
                            '$eq': ObjectId(data.noti_id)
                        }
                    },
                    {
                        'receiver_ids': {
                            '$elemMatch': {
                                '$eq': data2.get('user_id')
                            }
                        }
                    }
                ]      
            }
            update = {
                '$addToSet': {
                    'seen_ids': data2.get('user_id')
                }
            }
            # mark as seen
            noti_db[NOTI_COLLECTION].update_one(query, update)
        else:
            query = {
                '$and': [
                    {
                        'receiver_ids': {
                            '$elemMatch': {
                                '$eq': data2.get('user_id')
                            }
                        }
                    }
                ]          
            }
            update = {
                '$addToSet': {
                    'seen_ids': data2.get('user_id')
                }
            }

            # mark as seen
            noti_db[NOTI_COLLECTION].update_many(query, update)
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
        

#=================================================================
#======================ALL_UNREAD_NOTIFICATION====================
#=================================================================
@app.get(
    '/user_all_unread_notification',
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
async def user_all_unread_notification(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    data2: dict = Depends(valid_headers)
):
    # Find all noti unread
    logger().info('===========unread_message==========')
    try:
        num_skip = (page - 1)*limit
        pipeline=[
            {
                '$match': {
                    '$and': [
                        {
                            '$expr': {
                                '$in': [data2.get('user_id'), '$receiver_ids']
                            }
                        },
                        {
                            'removed_ids': {
                                '$not': {
                                    '$elemMatch': {
                                        '$eq': data2.get('user_id')
                                    }
                                }
                            }
                        },
                        {
                            'seen_ids': {
                                '$not': {
                                    '$elemMatch': {
                                        '$eq': data2.get('user_id')
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'users_profile',
                    'localField': 'sender_id',
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
                    'as': 'sender_data'
                }
            },
            {
                '$set': {
                    'sender_info': {
                        '$ifNull': [{'$first': '$sender_data'}, None]
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
                                'sender_info': 1,
                                'is_read': {
                                    '$in': [data2.get('user_id'), '$seen_ids']
                                },
                                "noti_type": 1,
                                "content": 1,
                                'target': 1,
                                'datetime_created': 1
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

        list_notification = noti_db[NOTI_COLLECTION].aggregate(pipeline)
        result_data, meta_data = get_data_and_metadata(aggregate_response=list_notification, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#=================================================================
#======================UPDATE_NOTIFICATION_SETTING================
#=================================================================
@app.put(
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
    data: DATA_Update_Notification_Setting,
    data2: dict = Depends(valid_headers)
):
    logger().info('===============initial_notification_setting=================')
    try:
        # insert to DB Notification Type Comment
        noti_db[NOTI_SETTING_COLLECTION].update_one(
            {
                'user_id': data2.get('user_id'),
                'noti_type': data.noti_type
            },
            {
                '$set': {
                    'is_enable': data.is_enable
                }
            },
            upsert=True
        )
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

