import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from app.utils.question_utils.question_exam import auto_pick_question
from configs.logger import logger
from configs.settings import (ANSWERS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, Path, Query, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from models.db.group import GroupQuestion
from models.db.question import Answers_DB, Questions_DB, Questions_Evaluation_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.question import ManageQuestionType
from models.request.exam import SaveExamConfig
from models.request.question import (DATA_Auto_Pick_Question, DATA_Create_Answer,
                                     DATA_Create_Fill_Question,
                                     DATA_Create_Matching_Question,
                                     DATA_Create_Multi_Choice_Question,
                                     DATA_Create_Sort_Question, DATA_Delete_Question, DATA_Evaluate_Question, DATA_Share_Question_To_Community, DATA_Share_Question_To_Group, DATA_Update_Question)
from starlette.responses import JSONResponse



#========================================================
#===================USER_GET_ALL_QUESTION================
#========================================================
@app.get(
    path='/user/get_all_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions']
)
async def user_get_all_question(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    type: Optional[str] = Query(default=None, description='question type'),
    level: Optional[str] = Query(default=None, description='question level'),
    tags: List[str] = Query(default=[], description='list tag_id'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        filter_question, filter_question_version = get_query_filter_questions(
            search=search,
            type=type,
            level=level,
            class_id=class_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            tags=tags
        )

        # =============== owner =================
        query_question_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_question.append(query_question_owner)


        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    '$and': filter_question_version
                }
            },
            {
                '$addFields': { # convert question_version_id in questions_version collection from ObjectId to String(to join with answers collection)
                    'question_version_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$addFields': { # convert question_id in questions_version collection from string to ObjectId(to join with questions collection)
                    'question_object_id': {
                        '$toObjectId': '$question_id'
                    }
                }
            },
            {
                '$lookup': { #join with questions collection
                    'from': 'questions',
                    'localField': 'question_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$match': {
                                '$and': filter_question
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'subject',
                                'let': {
                                    'subject_id': '$subject_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$subject_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'subject_info'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'class',
                                'let': {
                                    'class_id': '$class_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$class_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'class_info'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'let': {
                                    'chapter_id': '$chapter_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$chapter_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'chapter_info'
                            }
                        },
                        {
                            '$lookup': { #join with tag collection
                                'from': 'tag',
                                'let': {
                                    'list_tag_id': '$tag_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$id', '$$list_tag_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'tags_info'
                            }
                        },
                        {
                            '$addFields': {
                                'question_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'community_questions',
                                'let': {
                                    'question_id': '$question_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$question_id', '$$question_id']
                                            }
                                        }
                                    }
                                ],
                                'as': 'community_question_info'
                            }
                        },
                        {
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'level': 1,
                                'subject_info': {
                                    '$first': '$subject_info'
                                },
                                'class_info': {
                                    '$first': '$class_info'
                                },
                                'chapter_info': {
                                    '$first': '$chapter_info'
                                },
                                'tags_info': 1,
                                'is_public': {
                                    '$ne': ['$community_question_info', []]
                                },
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_information'
                }
            },
            {
                '$unwind': '$question_information'
            },
            {
                '$lookup': {
                    'from': 'questions_evaluation',
                    'let': {
                        'question_id': '$question_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$question_id', '$$question_id']
                                },
                                'user_id': data2.get('user_id')
                            }
                        },
                        {
                            '$sort': {
                                'datetime_created': -1
                            }
                        },
                        {
                            '$limit': 1
                        }
                    ],
                    'as': 'question_evaluation'
                }
            },   
            {
                '$set': {
                    'question_evaluation': {
                        '$ifNull': [{'$first': '$question_evaluation'}, {}]
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
                                'question_id': 1,
                                'question_version_id': {
                                    '$toString': '$_id'
                                },
                                'version_name': 1,
                                "question_content": 1,
                                'level': "$question_information.level",
                                'recommend_level': {
                                    '$ifNull': ['$question_evaluation.result', None]
                                },
                                'question_type': "$question_information.type",
                                'subject_info': "$question_information.subject_info",
                                'class_info': "$question_information.class_info",
                                'chapter_info': "$question_information.chapter_info",
                                'tags_info': "$question_information.tags_info",
                                'is_public': "$question_information.is_public",
                                'answers': 1,
                                'answers_right': 1,
                                'sample_answer': 1,
                                'display': 1,
                                'datetime_created': "$question_information.datetime_created"
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

        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=questions, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===================GROUP_GET_ALL_QUESTION================
#========================================================
@app.get(
    path='/group/get_all_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - group']
)
async def group_get_all_question(
    group_id: str = Query(..., description='ID of group'),
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    type: Optional[str] = Query(default=None, description='question type'),
    level: Optional[str] = Query(default=None, description='question level'),
    tags: List[str] = Query(default=[], description='list tag_id'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        #check group exist:
        if not check_group_exist(group_id=group_id):
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # check owner of group or member
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=group_id):
            raise Exception('user is not the owner or member of group!')


        filter_question, filter_question_version = get_query_filter_questions(
            search=search,
            type=type,
            level=level,
            class_id=class_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            tags=tags
        )

        # get list question of group
        list_question = get_list_group_question(group_id=group_id)
        # =============== list_group_exam =================
        query_question = {
            'question_id': {
                '$in': list_question
            }
        }
        filter_question_version.append(query_question)
        
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    '$and': filter_question_version
                }
            },
            {
                '$addFields': { # convert question_version_id in questions_version collection from ObjectId to String(to join with answers collection)
                    'question_version_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$addFields': { # convert question_id in questions_version collection from string to ObjectId(to join with questions collection)
                    'question_object_id': {
                        '$toObjectId': '$question_id'
                    }
                }
            },
            {
                '$lookup': { #join with questions collection
                    'from': 'questions',
                    'localField': 'question_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'question_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        # {
                        #     '$match': {
                        #         "$expr": {
                        #             '$in': ['$question_id', list_question]
                        #         }
                        #     }
                        # },
                        {
                            '$lookup': {
                                'from': 'group_questions',
                                'let': {
                                    'question_id': '$question_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$and': [
                                                {
                                                    '$expr': {
                                                        '$eq': ['$group_id', group_id]
                                                    }
                                                },
                                                {
                                                    '$expr': {
                                                        '$eq': ['$question_id', '$$question_id']
                                                    }
                                                },
                                            ]
                                        }
                                    }
                                ],
                                'as': 'group_question_info'
                            }
                        },
                        {
                            '$unwind': "$group_question_info"
                        },
                        {
                            '$set': {
                                'subject_id': '$group_question_info.subject_id',
                                'class_id': '$group_question_info.class_id',
                                'chapter_id': '$group_question_info.chapter_id',
                                'datetime_shared': '$group_question_info.datetime_created',
                            }
                        },
                        {
                            '$match': {
                                '$and': filter_question
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'tag',
                                'let': {
                                    'list_tag_id': '$tag_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$id', '$$list_tag_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'tags_info'
                            }
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
                                'as': 'author_data'
                            }
                        },
                        {
                            '$project': { #project for questions collection
                                '_id': 0,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'type': 1,
                                'level': 1,
                                'tags_info': 1,
                                'datetime_shared': 1,
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_information'
                }
            },
            {
                '$unwind': '$question_information'
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
                                'user_info': "$question_information.user_info",
                                'question_id': 1,
                                'question_version_id': {
                                    '$toString': '$_id'
                                },
                                'version_name': 1,
                                "question_content": 1,
                                'question_type': "$question_information.type",
                                'tags_info': "$question_information.tags_info",
                                'level': "$question_information.level",
                                'answers': 1,
                                'answers_right': 1,
                                'sample_answer': 1,
                                'display': 1,
                                'datetime_shared': "$question_information.datetime_shared",
                                'datetime_created': "$question_information.datetime_created"
                            }
                        },
                        {
                            '$sort': {
                                'datetime_shared': -1
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

        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=questions, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#================COMMUNITY_GET_ALL_QUESTION==============
#========================================================
@app.get(
    path='/community/get_all_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - community']
)
async def community_get_all_question(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    type: Optional[str] = Query(default=None, description='question type'),
    level: Optional[str] = Query(default=None, description='question level'),
    tags: List[str] = Query(default=[], description='list tag_id'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        filter_question, filter_question_version = get_query_filter_questions(
            search=search,
            type=type,
            level=level,
            class_id=class_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            tags=tags
        )

        # # =============== public =================
        # query_question_public = {
        #     'is_public': {
        #         '$eq': True
        #     }
        # }
        # filter_question.append(query_question_public)

        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    '$and': filter_question_version
                }
            },
            {
                '$addFields': { # convert question_version_id in questions_version collection from ObjectId to String(to join with answers collection)
                    'question_version_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$addFields': { # convert question_id in questions_version collection from string to ObjectId(to join with questions collection)
                    'question_object_id': {
                        '$toObjectId': '$question_id'
                    }
                }
            },
            {
                '$lookup': { #join with questions collection
                    'from': 'questions',
                    'localField': 'question_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'question_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        # {
                        #     '$match': {
                        #         "$expr": {
                        #             '$in': ['$question_id', list_question]
                        #         }
                        #     }
                        # },
                        {
                            '$lookup': {
                                'from': 'community_questions',
                                'let': {
                                    'question_id': '$question_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$question_id', '$$question_id']
                                            }
                                        }
                                    }
                                ],
                                'as': 'community_question_info'
                            }
                        },
                        {
                            '$unwind': "$community_question_info"
                        },
                        {
                            '$set': {
                                'subject_id': '$community_question_info.subject_id',
                                'class_id': '$community_question_info.class_id',
                                'chapter_id': '$community_question_info.chapter_id',
                                'datetime_shared': '$community_question_info.datetime_created',
                            }
                        },
                        {
                            '$match': {
                                '$and': filter_question
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'tag',
                                'let': {
                                    'list_tag_id': '$tag_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$id', '$$list_tag_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'tags_info'
                            }
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
                                'as': 'author_data'
                            }
                        },
                        {
                            '$project': { #project for questions collection
                                '_id': 0,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'type': 1,
                                'level': 1,
                                'tags_info': 1,
                                'datetime_shared': 1,
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_information'
                }
            },
            {
                '$unwind': '$question_information'
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
                                'user_info': "$question_information.user_info",
                                'question_id': 1,
                                'question_version_id': {
                                    '$toString': '$_id'
                                },
                                'version_name': 1,
                                "question_content": 1,
                                'question_type': "$question_information.type",
                                'tags_info': "$question_information.tags_info",
                                'level': "$question_information.level",
                                'answers': 1,
                                'answers_right': 1,
                                'sample_answer': 1,
                                'display': 1,
                                'datetime_shared': "$question_information.datetime_shared",
                                'datetime_created': "$question_information.datetime_created"
                            }
                        },
                        {
                            '$sort': {
                                'datetime_shared': -1
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

        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=questions, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#===========USER_GET_ALL_QUESTION_LIST_CHAPTER===========
#========================================================
@app.get(
    path='/user_get_questions_create_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - exam']
)
async def user_get_questions_create_exam(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    type: Optional[str] = Query(default=None, description='question type'),
    level: Optional[str] = Query(default=None, description='question level'),
    tags: List[str] = Query(default=[], description='list tag_id'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: List[str] = Query(default=[], description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        filter_question, filter_question_version = get_query_filter_questions(
            search=search,
            type=type,
            level=level,
            class_id=class_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            tags=tags
        )

        # =============== owner =================
        query_question_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_question.append(query_question_owner)


        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    '$and': filter_question_version
                }
            },
            {
                '$addFields': { # convert question_version_id in questions_version collection from ObjectId to String(to join with answers collection)
                    'question_version_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$addFields': { # convert question_id in questions_version collection from string to ObjectId(to join with questions collection)
                    'question_object_id': {
                        '$toObjectId': '$question_id'
                    }
                }
            },
            {
                '$lookup': { #join with questions collection
                    'from': 'questions',
                    'localField': 'question_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$match': {
                                '$and': filter_question
                            }
                        },
                        {
                            '$lookup': { #join with tag collection
                                'from': 'tag',
                                'let': {
                                    'list_tag_id': '$tag_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$id', '$$list_tag_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'tags_info'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'subject',
                                'let': {
                                    'subject_id': '$subject_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$subject_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'subject_info'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'class',
                                'let': {
                                    'class_id': '$class_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$class_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'class_info'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'let': {
                                    'chapter_id': '$chapter_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$chapter_id']
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': 1,
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'chapter_info'
                            }
                        },
                        {
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'level': 1,
                                'tags_info': 1,
                                'subject_info': {
                                    '$first': '$subject_info'
                                },
                                'class_info': {
                                    '$first': '$class_info'
                                },
                                'chapter_info': {
                                    '$first': '$chapter_info'
                                },
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_information'
                }
            },
            {
                '$unwind': '$question_information'
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
                                'question_id': 1,
                                'question_version_id': {
                                    '$toString': '$_id'
                                },
                                'version_name': 1,
                                "question_content": 1,
                                "question_image": 1,
                                'subject_info': "$question_information.subject_info",
                                'class_info': "$question_information.class_info",
                                'chapter_info': "$question_information.chapter_info",
                                'level': "$question_information.level",
                                'question_type': "$question_information.type",
                                'tags_info': "$question_information.tags_info",
                                'answers': 1,
                                'answers_right': 1,
                                'sample_answer': 1,
                                'display': 1,
                                'datetime_created': "$question_information.datetime_created"
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

        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=questions, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#===============USER_AUTO_PICK_QUESTIONS=================
#========================================================
@app.post(
    path='/user_auto_pick_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - exam']
)
async def user_auto_pick_question(
    data: List[DATA_Auto_Pick_Question],
    data2: dict = Depends(valid_headers)
):
    try:
        result = []
        result_id = []
        for selec in data:
            flag = True
            while flag:
                pipeline_head = [
                    {
                        '$set': {
                            '_id': {
                                '$toString': '$_id'
                            }
                        }
                    },
                    {
                        '$match': {
                            'chapter_id': selec.chapter_id,
                            'type': {
                                '$in': selec.type
                            },
                            '_id': {
                                '$not': {
                                    '$in': result_id
                                }
                            }
                        }
                    }
                ]
                facet_body = {}
                for key in selec.level.keys():
                    if selec.level.get(key):
                        facet_body[key] = [
                            {
                                '$match': {
                                    'level': key
                                }
                            },
                            {
                                '$sample': {
                                    'size': selec.level.get(key)
                                }
                            },
                            {
                                '$group': {
                                    '_id': {
                                        '$toString': '$_id'
                                    },
                                    'user_id': {
                                        '$first': '$user_id'
                                    },
                                    'subject_id': {
                                        '$first': '$subject_id'
                                    },
                                    'class_id': {
                                        '$first': '$class_id'
                                    },
                                    'chapter_id': {
                                        '$first': '$chapter_id'
                                    },
                                    'type': {
                                        '$first': '$type'
                                    },
                                    'tag_id': {
                                        '$first': '$tag_id'
                                    },
                                    'level': {
                                        '$first': '$level'
                                    },
                                    'datetime_created': {
                                        '$first': '$datetime_created'
                                    },
                                }
                            }
                        ]

                pipeline_facet = [
                    {
                        '$facet': facet_body
                    }
                ]

                pipeline = pipeline_head + pipeline_facet
                res_data = questions_db[QUESTIONS].aggregate(pipeline)
                flag = False
                if res_data.alive:
                    res_data = res_data.next()
                    logger().info(f'res_data; {res_data}')

                    more_data = []
                    for key in selec.level.keys():
                        if res_data.get(key):
                            more_data += res_data.get(key)
                            selec.level[key] = selec.level.get(key) - len(res_data.get(key))
                        if selec.level[key]:
                            flag = True
                    logger().info(more_data)
                    logger().info(selec.level)
                    if more_data:
                        result += more_data
                        for x in more_data:
                            result_id.append(x.get('_id'))
                    else:
                        raise Exception(f'not have enough question in chapter {selec.chapter_id}!')
                    logger().info(result_id)
                else:
                    raise Exception('error occur!')
                
        pipeline = [
            {
                '$set': {
                    'question_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$match': {
                    'question_id': {
                        '$in': result_id
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'tag',
                    'let': {
                        'list_tag_id': '$tag_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$in': ['$id', '$$list_tag_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'tags_info'
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'let': {
                        'subject_id': '$subject_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$subject_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'subject_info'
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'let': {
                        'class_id': '$class_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$class_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'class_info'
                }
            },
            {
                '$lookup': {
                    'from': 'chapter',
                    'let': {
                        'chapter_id': '$chapter_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$chapter_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'chapter_info'
                }
            },
            {
                '$lookup': {
                    'from': 'questions_version',
                    'localField': 'question_id',
                    'foreignField': 'question_id',
                    'pipeline': [
                        {
                            '$match' : {
                                'is_latest': True
                            }
                        }
                    ],
                    'as': 'ques_ver'
                }
            },
            {
                '$unwind': '$ques_ver'
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'subject_info': {
                        '$first': '$subject_info'
                    },
                    'class_info': {
                        '$first': '$class_info'
                    },
                    'chapter_info': {
                        '$first': '$chapter_info'
                    },
                    'level': 1,
                    'question_id': 1,
                    'question_version_id': {
                        '$toString': '$ques_ver._id'
                    },
                    'version_name': '$ques_ver.version_name',
                    "question_content": '$ques_ver.question_content',
                    # "question_image": '$ques_ver.question_image',
                    'question_type': "$type",
                    'tags_info': "$tags_info",
                    'answers': '$ques_ver.answers',
                    'answers_right': '$ques_ver.answers_right',
                    'sample_answer': '$ques_ver.sample_answer',
                    'display': '$ques_ver.display',
                    'datetime_created': "$datetime_created"
                }
            },
            {
                '$group': {
                    '_id': None,
                    'data': {
                        '$push': '$$ROOT'
                    }
                }
            }
        ]
        question_data = questions_db[QUESTIONS].aggregate(pipeline)
        if question_data.alive:
            result_data = question_data.next()
            result_data = result_data.get('data')
        else:
            raise Exception('error occur!')
        
        return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg="Có lỗi xảy ra!"
        return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===============EXAM_AUTO_GENERATE_QUESTIONS=============
#========================================================
@app.post(
    path='/exam_auto_generate_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - exam']
)
async def exam_auto_generate_question(
    data: List[SaveExamConfig],
    data2: dict = Depends(valid_headers)
):
    try:
        for section in data:
            section['section_questions'] = auto_pick_question(data=section.get('section_questions'))
        
        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg="Có lỗi xảy ra!"
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)



#========================================================
#===========USER_GET_LIST_QUESTION_EVALUATION============
#========================================================
@app.get(
    path='/user_get_questions_evaluation',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - evaluation']
)
async def user_get_questions_evaluation(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    # search: Optional[str] = Query(default=None, description='text search'),
    question_id: Optional[str] = Query(..., description='ID of question'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    'question_id': question_id,
                    'user_id': data2.get('user_id')
                }
            },
            {
                '$lookup': {
                    'from': 'questions',
                    'pipeline': [
                        {
                            '$set': {
                                'question_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                'question_id': question_id
                            }
                        }
                    ],
                    'as': 'question_info'
                }
            },
            {
                '$set': {
                    'question_info': {
                        '$ifNull': [{'$first': '$question_info'}, {}]
                    }
                }
            },
            {
                '$set': {
                    'old_level': {
                        '$ifNull': ['$question_info.level', None]
                    },
                    # 'is_owner': {
                    #     '$eq': ['$question_info.user_id', data2.get('user_id')]
                    # }
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
                                'user_id': 0,
                                # 'evaluation_id': 0,
                                # 'datetime_created': 0,
                                'question_info': 0,
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

        questions = questions_db[QUESTIONS_EVALUATION].aggregate(pipeline)

        result_data, meta_data = get_data_and_metadata(aggregate_response=questions, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


