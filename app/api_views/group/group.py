#  Copyright (c) 2021.
from datetime import datetime
from math import ceil
from typing import Optional
from app.utils.group_utils.group import check_group_exist, check_owner_of_group
from app.utils.question_utils.question import get_data_and_metadata
from configs.settings import GROUP_QUESTIONS
from models.db.group import Group_DB, GroupMember

from bson import ObjectId
from fastapi import BackgroundTasks, Depends, Path, Query, status
from fastapi.responses import JSONResponse

from configs import GROUP, GROUP_PARTICIPANT, app, group_db
from models.define.group import GroupStatus, UpdateGroupImage
from models.request.group import DATA_Create_Group, DATA_Delete_Group, DATA_Leave_Group, DATA_Remove_Group_Question, DATA_Remove_Members, DATA_Update_Group, DATA_Update_Group_image
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
        group = check_group_exist(group_id=data.group_id)
        if group:
            # check owner of group
            if not check_owner_of_group(user_id=data2.get('user_id'), group_id=data.group_id):
                raise Exception('user is not owner of group!')

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

#=================================================================
#==========================DELETE_GROUP===========================
#=================================================================
@app.delete(
    '/remove_group',
    description='remove group',
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
    try:
        # Find a group
        group = check_group_exist(group_id=data.group_id)
        if group:
            query_owner = {
                'group_id': data.group_id,
                'user_id': data2.get('user_id'),
                'is_owner': True
            }
            group_owner = group_db[GROUP_PARTICIPANT].find_one(query_owner)
            if not group_owner:
                raise Exception('user is not the owner of group!')
            
            # remove group_participant
            # query_participant = {
            #     'group_id': data.group_id,
            # }
            # group_db.get_collection('group_participant').delete_many(query_participant)

            # update group in DB
            group_db[GROUP].find_one_and_update(
                {
                    '_id': ObjectId(data.group_id)
                },
                {
                    '$set': {
                        'is_deleted': True
                    }
                }
            )
            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

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
        query_filter = {
            '$and': [
                
            ] 
        }

        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(group_id)
                }
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
                    'is_owner': {
                        '$first': '$members_participant.is_owner'
                    }
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
                    'num_members': {
                        '$size': '$member_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_questions',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'questions_in_group'
                }
            },
            {
                '$set': {
                    'num_questions': {
                        '$size': '$questions_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_exams',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'exams_in_group'
                }
            },
            {
                '$set': {
                    'num_exams': {
                        '$size': '$exams_in_group'
                    } 
                }
            },
            {
                '$project': {
                    'member_in_group': 0,
                    'owner_id': 0,
                    'group_status': 0,
                    'members_participant': 0,
                    'questions_in_group': 0,
                    'exams_in_group': 0,
                    'invitation': 0,
                    'request_join': 0,
                    'is_approved': 0,
                    'is_deleted': 0
                }
            }
        ]
        group_data = group_db[GROUP].aggregate(pipeline)
        logger().info(group_data.alive)
        if group_data.alive:
            result_data = group_data.next()
            return JSONResponse(content={'status': 'success', 'data': result_data}, status_code=status.HTTP_200_OK)
        else:
            msg = 'group not found!'
            return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed!', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

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
                    'num_members': {
                        '$size': '$member_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_questions',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'questions_in_group'
                }
            },
            {
                '$set': {
                    'num_questions': {
                        '$size': '$questions_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_exams',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'exams_in_group'
                }
            },
            {
                '$set': {
                    'num_exams': {
                        '$size': '$exams_in_group'
                    } 
                }
            },
            {
                '$project': {
                    'member_in_group': 0,
                    'owner_id': 0,
                    'group_status': 0,
                    'members_participant': 0,
                    'questions_in_group': 0,
                    'exams_in_group': 0,
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
                    'num_members': {
                        '$size': '$member_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_questions',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'questions_in_group'
                }
            },
            {
                '$set': {
                    'num_questions': {
                        '$size': '$questions_in_group'
                    } 
                }
            },
            {
                '$lookup': {
                    'from': 'group_exams',
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
                        # {
                        #     '$set': {
                        #         '_id': {'$toString': '$_id'},
                        #     }
                        # }
                    ],
                    'as':'exams_in_group'
                }
            },
            {
                '$set': {
                    'num_exams': {
                        '$size': '$exams_in_group'
                    } 
                }
            },
            {
                '$project': {
                    'member_in_group': 0,
                    'owner_id': 0,
                    'group_status': 0,
                    'members_participant': 0,
                    'questions_in_group': 0,
                    'exams_in_group': 0,
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
#=======================USER_LEAVE_GROUP==========================
#=================================================================
@app.post(
    '/user_leave_group',
    description='user leave group',
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
async def user_leave_group(
    data: DATA_Leave_Group,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============user_leave_group=================')
    """
    
    """
    try:
        # delete mem
        query_mem = {
            'group_id': data.group_id,
            'user_id': data2.get('user_id'),
        }
        mem_data = group_db[GROUP_PARTICIPANT].find_one_and_delete(query_mem)
        if mem_data:
            # check if group still have participant
            count_mem = group_db[GROUP_PARTICIPANT].find({'group_id': data.group_id}).count()
            if not count_mem:
                # remove group
                group_db[GROUP].update_one({'_id': ObjectId(data.group_id)}, {'$set': {'is_deleted': True}})
                msg = 'no members left, group is removed!'
                return JSONResponse(content={'status': 'success', 'msg': msg}, status_code=status.HTTP_200_OK)

            # check user is group owner
            if mem_data.get('is_owner'):
                # update new owner
                new_owner = group_db[GROUP_PARTICIPANT].find_one_and_update({'group_id': data.group_id}, {'$set': {'is_owner': True}}, sort=[('datetime_created', -1)])
                ################################################
                # broadcast to new owner
                ################################################

            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
        else:
            msg = 'Error, user is not member of group!!!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#=================================================================
#====================USER_REMOVE_GROUP_QUESTION===================
#=================================================================
@app.delete(
    '/remove_group_question',
    description='user remove group question',
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
async def remove_group_question(
    data: DATA_Remove_Group_Question,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============user_remove_group_question=================')
    try:
        # find member
        query_mem = {
            'group_id': data.group_id,
            'user_id': data2.get('user_id'),
        }
        mem_data = group_db[GROUP_PARTICIPANT].find_one(query_mem)
        if mem_data:
            # find question
            query_question = {
                'group_id': data.group_id,
                'question_id': data.question_id
            }
            question_data = group_db[GROUP_QUESTIONS].find_one(query_question)
            if not question_data:
                msg = 'question not found!'
                return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

            # check user is group owner or sharer
            if mem_data.get('is_owner') or (question_data.get('sharer_id') == data2.get('user_id')):
                # delete group question
                group_db[GROUP_QUESTIONS].delete_one(query_question)
            else:
                raise Exception('user is not owner of group or sharer!')

            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
        else:
            raise Exception('user is not member of group!!!')        
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



