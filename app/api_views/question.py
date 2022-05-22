from math import ceil
import copy
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_chapter_info, get_class_info, get_subject_info
from app.utils.group_utils.group import check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_answer
from bson import ObjectId
from configs.logger import logger
from configs.settings import (ANSWERS, QUESTIONS, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db)
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.question import Answers_DB, Questions_DB, Questions_Version_DB
from models.define.question import ManageQuestionType
from models.request.question import (DATA_Create_Answer,
                                     DATA_Create_Fill_Question,
                                     DATA_Create_Matching_Question,
                                     DATA_Create_Multi_Choice_Question,
                                     DATA_Create_Sort_Question)
from starlette.responses import JSONResponse


#========================================================
#=============CREATE__MULTI_CHOICE_QUESTION==============
#========================================================
@app.post(
    path='/create_multi_choice_question',
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
async def create_multi_choice_question(
    data1: DATA_Create_Multi_Choice_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # check user
        user = SYSTEM['users'].find_one(
            {
                'email': {
                    '$eq': data2.get('email')
                }
            }
        )
        if not user:
            return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.MULTICHOICE,
            tag_id=data1.get('tag_id'),
            level=data1.get('level'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=================CREATE_MATCHING_QUESTION===============
#========================================================
@app.post(
    path='/create_matching_question',
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
async def create_matching_question(
    data1: DATA_Create_Matching_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.MATCHING,
            tag_id=data1.get('tag_id'),
            level=data1.get('level'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#==================CREATE_SORT_QUESTION==================
#========================================================
@app.post(
    path='/create_sort_question',
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
async def create_sort_question(
    data1: DATA_Create_Sort_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.SORT,
            tag_id=data1.get('tag_id'),
            level=data1.get('level'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#==================CREATE_FILL_QUESTION==================
#========================================================
@app.post(
    path='/create_fill_question',
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
async def create_fill_question(
    data1: DATA_Create_Fill_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.FILL,
            tag_id=data1.get('tag_id'),
            level=data1.get('level'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=====================CREATE_ANSWER======================
#========================================================
@app.post(
    path='/create_answer',
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
async def create_answer(
    data1: DATA_Create_Answer,
    data2: dict = Depends(valid_headers)
):
    try:
        data1 = jsonable_encoder(data1)
        
        answer = Answers_DB(
            answer_content=data1.get('answer_content'),
            answer_image=data1.get('answer_image'),
        )


        # insert to answers table
        id_answer = questions_db[ANSWERS].insert_one(jsonable_encoder(answer)).inserted_id

        answer = jsonable_encoder(answer)
        answer.update({'answer_id': str(id_answer)})

        return JSONResponse(content={'status': 'success', 'data': answer},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#===================USER_GET_ONE_QUESTION================
#========================================================
@app.get(
    path='/user/get_one_question/{question_id}',
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
async def user_get_one_question(
    question_id: str = Path(..., description='ID of question'),
    data2: dict = Depends(valid_headers)
):
    try:
        # find question
        question = questions_db[QUESTIONS].find_one(
            {
                "$and": [
                    {
                        '_id': ObjectId(question_id)
                    },
                    {
                        'user_id': {
                            '$eq': data2.get('user_id')
                        }
                    },
                    {
                        'is_removed': False
                    }
                ]
                        
            }
        )
        if not question:
            return JSONResponse(content={'status': 'Question not found!'}, status_code=status.HTTP_404_NOT_FOUND)
        
        # find question version
        question_version = questions_db[QUESTIONS_VERSION].find_one(
            {
                '$and': [
                    {
                        'question_id': question_id
                    },
                    {
                        'is_latest': True
                    }
                ]
            }
        )
        if not question_version:
            return JSONResponse(content={'status': 'Question not found!'}, status_code=status.HTTP_404_NOT_FOUND)

        # get answer of question
        answers = get_answer(answers=question_version.get('answers'), question_type=question.get('type'))

        logger().info(answers)
        question_version['answers'] = answers
        del question['_id']
        del question_version['_id']
        question['question_info'] = question_version

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

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
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        filter_question = [{}]
        filter_question_version = [{}]

        # =============== search =================
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter_question_version.append(query_search)
        
        # =============== version =================
        query_latest_version = {
            'is_latest': True
        }
        filter_question_version.append(query_latest_version)

        # =============== status =================
        query_question_status = {
            'is_removed': False
        }
        filter_question.append(query_question_status)

        # =============== owner =================
        query_question_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_question.append(query_question_owner)

        # =============== type =================
        if type:
            query_question_type = {
                'type': type
            }
            filter_question.append(query_question_type)

        # =============== level =================
        if level:
            query_question_level = {
                'level': level
            }
            filter_question.append(query_question_level)

        # =============== class =================
        if class_id:
            query_question_class = {
                'class_id': class_id
            }
            filter_question.append(query_question_class)

        # =============== subject =================
        if subject_id:
            query_question_subject = {
                'subject_id': subject_id
            }
            filter_question.append(query_question_subject)

        # =============== chapter =================
        if chapter_id:
            query_question_chapter = {
                'chapter_id': chapter_id
            }
            filter_question.append(query_question_chapter)

        num_skip = (page - 1)*limit

        # pipeline = [
        #     {
        #         '$addFields': {
        #             'question_id': {
        #                 '$toString': '$_id'
        #             }
        #         }
        #     },
        #     {
        #         '$lookup': {
        #             'from': 'questions_version',
        #             'localField': 'question_id',
        #             'foreignField': 'question_id',
        #             'pipeline': [
        #                 {
        #                     '$match': {
        #                         '$and': filter_question_version
        #                     }
        #                 }
        #             ],
        #             'as': 'question_information'
        #         }
        #     },
        #     {
        #         '$unwind': '$question_information'
        #     },
        #     {
        #         '$match': {
        #             '$and': filter_question
        #         }
        #     },
        #     {
        #         '$project': {
        #             '_id': 0,
        #             'question_id': 1,
        #             'type': 1,
        #             'level': 1,
        #             'datetime_created': 1,
        #             'question_information.question_content': 1,
        #             'question_information.question_image': 1,
        #             'question_information.answers': 1,
        #             'question_information.correct_answers': 1
        #         }
        #     },
        #     { "$skip": num_skip },
        #     { "$limit": limit }
        # ]

        # pipeline_all = [
        #     {
        #         '$addFields': {
        #             'question_id': {
        #                 '$toString': '$_id'
        #             }
        #         }
        #     },
        #     {
        #         '$lookup': {
        #             'from': 'questions_version',
        #             'localField': 'question_id',
        #             'foreignField': 'question_id',
        #             'pipeline': [
        #                 {
        #                     '$match': {
        #                         '$and': filter_question_version
        #                     }
        #                 }
        #             ],
        #             'as': 'question_information'
        #         }
        #     },
        #     {
        #         '$unwind': '$question_information'
        #     },
        #     {
        #         '$match': {
        #             '$and': filter_question
        #         }
        #     },
        #     { '$group': { '_id': None, 'myCount': { '$sum': 1 } } },
        #     { '$project': { '_id': 0 } }
        # ]

        # pipeline = [
        #     {
        #         '$addFields': {
        #             'question_id': {
        #                 '$toString': '$_id'
        #             }
        #         }
        #     },
        #     {
        #         '$lookup': {
        #             'from': 'questions_version',
        #             'localField': 'question_id',
        #             'foreignField': 'question_id',
        #             'pipeline': [
        #                 {
        #                     '$match': {
        #                         '$and': filter_question_version
        #                     }
        #                 }
        #             ],
        #             'as': 'question_information'
        #         }
        #     },
        #     {
        #         '$unwind': '$question_information'
        #     },
        #     {
        #         '$match': {
        #             '$and': filter_question
        #         }
        #     },
                        
        #     { 
        #         '$facet' : {
        #             'metadata': [ 
        #                 { 
        #                     '$count': "total" 
        #                 }, 
        #                 { 
        #                     '$addFields': { 
        #                         'page': {
        #                             '$toInt': {
        #                                 '$ceil': {
        #                                     '$divide': ['$total', limit]
        #                                 }
        #                             }
        #                         }
        #                     } 
        #                 } 
        #             ],
        #             'data': [ 
        #                 {
        #                     '$project': {
        #                         '_id': 0,
        #                         'question_id': 1,
        #                         'type': 1,
        #                         'level': 1,
        #                         'datetime_created': 1,
        #                         'question_information.question_content': 1,
        #                         'question_information.question_image': 1,
        #                         'question_information.answers': 1,
        #                         'question_information.correct_answers': 1
        #                     }
        #                 },
        #                 { 
        #                     '$skip': num_skip 
        #                 },
        #                 { 
        #                     '$limit': limit 
        #                 } 
        #             ] # add projection here wish you re-shape the docs
        #         } 
        #     },
        #     {
        #         '$unwind': '$metadata'
        #     },
        #     # {
        #     #     '$unwind': '$data'
        #     # }
        #     # {
        #     #     '$group': {
        #     #         '_id': None,
        #     #         'metadata': {
        #     #             '$first': {
        #     #                 '$first': '$metadata'
        #     #             }
        #     #         },
        #     #         'data': {
        #     #             '$first': {
        #     #                 '$first': '$data'
        #     #             }
        #     #         }
        #     #     }
        #     # }
        # ]
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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
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
                '$lookup': { # join to find answer of question
                    'from': 'answers',
                    'let': {'answers': '$answers'},
                    'pipeline': [
                        {
                            "$addFields": { "answer_id": { "$toString": "$_id" }}
                        },
                        {
                            "$match": { "$expr": { "$in": [ "$answer_id", "$$answers" ] } }
                        },
                        {
                            '$project': { #project for answers infomation
                                '_id': 0,
                                'answer_id': 1,
                                'answer_content': 1,
                                'answer_image': 1,
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_answers'
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
                                "question_content": 1,
                                "question_image": 1,
                                'question_type': "$question_information.type",
                                'question_answers': 1,
                                'question_correct_answers': "$question_answers.corect_answers",
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

        result = []

        # questions = questions_db[QUESTIONS].aggregate(pipeline)
        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        # all_questions = questions_db[QUESTIONS].aggregate(pipeline_all)

        # find question
        # questions = questions_db[QUESTIONS].find(
        #     {
        #         "$and": [
        #             {
        #                 'user_id': {
        #                     '$eq': data2.get('user_id')
        #                 }
        #             },
        #             {
        #                 'is_removed': False
        #             }
        #         ]
                        
        #     }
        # )
        # logger().info(type(questions2))
        questions_data = questions.next()
        # logger().info(questions2.next())
        
        # count_question = all_questions.next()
        # num_question = count_question.get('myCount')
        # num_pages = ceil(num_question/limit)
        
        # for question in questions_data.get('data'):
        #     # logger().info(question)
        #     # get answer of question
        #     answers = get_answer(answers=question['question_information'].get('answers'), question_type=question.get('type'))

        #     logger().info(answers)
        #     question['question_information']['answers'] = answers
        #     result.append(question)

        questions_count = questions_data['metadata']['total']
        num_pages = questions_data.get('metadata').get('page')
        
        meta_data = {
            'count': questions_count,
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }
            # # find question version
            # question_version = questions_db[QUESTIONS_VERSION].find_one(
            #     {
            #         '$and': [
            #             {
            #                 'question_id': str(question['_id'])
            #             },
            #             {
            #                 'is_latest': True
            #             }
            #         ]
            #     }
            # )
            # if question_version:
            #     # get answer of question
            #     answers = get_answer(answers=question_version.get('answers'), question_type=question.get('type'))

            #     logger().info(answers)
            #     question_version['answers'] = answers
            #     del question['_id']
            #     del question_version['_id']
            #     question['question_info'] = question_version
            #     result.append(question)
            # else:
            #     del question['_id']
            #     question['question_info'] = {}
            #     result.append(question)

        logger().info(result)
        return JSONResponse(content={'status': 'success', 'data': questions_data['data'], 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#================USER_GET_QUESTION_CLASSIFY==============
#========================================================
@app.get(
    path='/user/get_question_classify',
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
async def user_get_question_classify(
    data2: dict = Depends(valid_headers)
):
    try:
        filter_question = [{}]

        # =============== status =================
        query_question_status = {
            'is_removed': False
        }
        filter_question.append(query_question_status)

        # =============== owner =================
        query_question_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_question.append(query_question_owner)

        pipeline = [
            {
                '$match': {
                    '$and': filter_question
                }
            },
            {
                '$group': {
                    '_id': None,
                    'subject': {
                        '$addToSet': '$subject_id'
                    }
                }
            }
        ]

        result = []

        questions = questions_db[QUESTIONS].aggregate(pipeline)
        
        questions_data = questions.next()
        logger().info(f'questions_data: {questions_data}')
        # get class of subject
        data_return = []
        for subject_id in questions_data['subject']:
            filter_class = copy.deepcopy(filter_question)
            query_subject = {
                'subject_id': subject_id
            }
            filter_class.append(query_subject)

            pipeline_class = [
                {
                    '$match': {
                        '$and': filter_class
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'class': {
                            '$addToSet': '$class_id'
                        }
                    }
                }
            ]
            questions_class = questions_db[QUESTIONS].aggregate(pipeline_class)
            questions_class_data = questions_class.next()

            subject_data_class = []
            # get chapter of class, subject
            for class_id in questions_class_data['class']:
                filter_chapter = copy.deepcopy(filter_class)
                query_class = {
                    'class_id': class_id
                }
                filter_chapter.append(query_class)

                pipeline_chapter = [
                    {
                        '$match': {
                            '$and': filter_chapter
                        }
                    },
                    {
                        '$group': {
                            '_id': None,
                            'chapter': {
                                '$addToSet': '$chapter_id'
                            }
                        }
                    }
                ]
                questions_chapter = questions_db[QUESTIONS].aggregate(pipeline_chapter)
                questions_chapter_data = questions_chapter.next()

                class_data_chapter = []
                for chapter_id in questions_chapter_data['chapter']:
                    chapter_info = get_chapter_info(chapter_id=chapter_id)
                    data_chapter = {
                        'id': chapter_info.get('_id'),
                        'name': chapter_info.get('name')
                    }
                    class_data_chapter.append(data_chapter)
                
                class_info = get_class_info(class_id=class_id)
                data_class = {
                    'id': class_info.get('_id'),
                    'name': class_info.get('name'),
                    'chapters': class_data_chapter
                }
                subject_data_class.append(data_class)
            
            subject_info = get_subject_info(subject_id=subject_id)
            data_subject = {
                'id': subject_info.get('_id'),
                'name': subject_info.get('name'),
                'classes': subject_data_class
            }
            data_return.append(data_subject)
          
        logger().info(result)
        return JSONResponse(content={'status': 'success', 'data': data_return},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

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
    tags=['questions']
)
async def group_get_all_question(
    group_id: str = Query(..., description='ID of group'),
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    type: Optional[str] = Query(default=None, description='question type'),
    level: Optional[str] = Query(default=None, description='question level'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of group or member
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=group_id):
            content = {'status': 'Failed', 'msg': 'User is not the owner or member of group'}
            return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

        # get list question of group
        list_question = get_list_group_question(group_id=group_id)

        filter_question = [{}]
        filter_question_version = [{}]

        # =============== search =================
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter_question_version.append(query_search)
        
        # =============== version =================
        query_latest_version = {
            'is_latest': True
        }
        filter_question_version.append(query_latest_version)

        # =============== status =================
        query_question_status = {
            'is_removed': False
        }
        filter_question.append(query_question_status)

        # =============== owner =================
        query_question_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_question.append(query_question_owner)

        # =============== type =================
        if type:
            query_question_type = {
                'type': type
            }
            filter_question.append(query_question_type)

        # =============== level =================
        if level:
            query_question_level = {
                'level': level
            }
            filter_question.append(query_question_level)

        # =============== class =================
        if class_id:
            query_question_class = {
                'class_id': class_id
            }
            filter_question.append(query_question_class)

        # =============== subject =================
        if subject_id:
            query_question_subject = {
                'subject_id': subject_id
            }
            filter_question.append(query_question_subject)

        # =============== chapter =================
        if chapter_id:
            query_question_chapter = {
                'chapter_id': chapter_id
            }
            filter_question.append(query_question_chapter)

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
                            '$project': { #project for questions collection
                                '_id': 0,
                                'type': 1,
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
                '$lookup': { # join to find answer of question
                    'from': 'answers',
                    'let': {'answers': '$answers'},
                    'pipeline': [
                        {
                            "$addFields": { "answer_id": { "$toString": "$_id" }}
                        },
                        {
                            "$match": { "$expr": { "$in": [ "$answer_id", "$$answers" ] } }
                        },
                        {
                            '$project': { #project for answers infomation
                                '_id': 0,
                                'answer_id': 1,
                                'answer_content': 1,
                                'answer_image': 1,
                                'datetime_created': 1
                            }
                        }
                    ],
                    'as': 'question_answers'
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
                                "question_content": 1,
                                "question_image": 1,
                                'question_type': "$question_information.type",
                                'question_answers': 1,
                                'question_correct_answers': "$question_answers.corect_answers",
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

        result = []

        # questions = questions_db[QUESTIONS].aggregate(pipeline)
        questions = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        # all_questions = questions_db[QUESTIONS].aggregate(pipeline_all)

        # find question
        # questions = questions_db[QUESTIONS].find(
        #     {
        #         "$and": [
        #             {
        #                 'user_id': {
        #                     '$eq': data2.get('user_id')
        #                 }
        #             },
        #             {
        #                 'is_removed': False
        #             }
        #         ]
                        
        #     }
        # )
        # logger().info(type(questions2))
        questions_data = questions.next()
        # logger().info(questions2.next())
        
        # count_question = all_questions.next()
        # num_question = count_question.get('myCount')
        # num_pages = ceil(num_question/limit)
        
        # for question in questions_data.get('data'):
        #     # logger().info(question)
        #     # get answer of question
        #     answers = get_answer(answers=question['question_information'].get('answers'), question_type=question.get('type'))

        #     logger().info(answers)
        #     question['question_information']['answers'] = answers
        #     result.append(question)

        questions_count = questions_data['metadata']['total']
        num_pages = questions_data.get('metadata').get('page')
        
        meta_data = {
            'count': questions_count,
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }
            # # find question version
            # question_version = questions_db[QUESTIONS_VERSION].find_one(
            #     {
            #         '$and': [
            #             {
            #                 'question_id': str(question['_id'])
            #             },
            #             {
            #                 'is_latest': True
            #             }
            #         ]
            #     }
            # )
            # if question_version:
            #     # get answer of question
            #     answers = get_answer(answers=question_version.get('answers'), question_type=question.get('type'))

            #     logger().info(answers)
            #     question_version['answers'] = answers
            #     del question['_id']
            #     del question_version['_id']
            #     question['question_info'] = question_version
            #     result.append(question)
            # else:
            #     del question['_id']
            #     question['question_info'] = {}
            #     result.append(question)

        logger().info(result)
        return JSONResponse(content={'status': 'success', 'data': questions_data['data'], 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
