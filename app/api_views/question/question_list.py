import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from configs.logger import logger
from configs.settings import (ANSWERS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, Path, Query, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from models.db.group import GroupQuestion
from models.db.question import Answers_DB, Questions_DB, Questions_Evaluation_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.question import ManageQuestionType
from models.request.question import (DATA_Create_Answer,
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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'level': 1,
                                'tags_info': 1,
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

        # get list question of group
        list_question = get_list_group_question(group_id=group_id)

        filter_question, filter_question_version = get_query_filter_questions(
            search=search,
            type=type,
            level=level,
            class_id=class_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            tags=tags
        )

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
                        {
                            '$match': {
                                "$expr": {
                                    '$in': ['$question_id', list_question]
                                }
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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'tags_info': 1,
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
                                "question_content": 1,
                                "question_image": 1,
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

        # =============== public =================
        query_question_public = {
            'is_public': {
                '$eq': True
            }
        }
        filter_question.append(query_question_public)

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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'tags_info': 1,
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
                                "question_content": 1,
                                "question_image": 1,
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
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)


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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
                                'level': 1,
                                'tags_info': 1,
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

