import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value
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
from models.define.target import ManageTargetType
from models.request.question import (DATA_Create_Answer,
                                     DATA_Create_Fill_Question,
                                     DATA_Create_Matching_Question,
                                     DATA_Create_Multi_Choice_Question,
                                     DATA_Create_Sort_Question, DATA_Delete_Question, DATA_Evaluate_Question, DATA_Share_Question_To_Community, DATA_Share_Question_To_Group, DATA_Update_Question)
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
            tag_id=get_list_tag_id_from_input(data1.get('tag_id')),
            level=data1.get('level'),
            datetime_created=datetime.now().timestamp()
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
            # correct_answers=data1.get('correct_answers'),
            display=data1.get('display'),
            datetime_created=datetime.now().timestamp()
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
            tag_id=get_list_tag_id_from_input(data1.get('tag_id')),
            level=data1.get('level'),
            datetime_created=datetime.now().timestamp()
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
            answers_right=data1.get('answers_right'),
            sample_answer=data1.get('sample_answer'),
            display=data1.get('display'),
            datetime_created=datetime.now().timestamp()
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
            tag_id=get_list_tag_id_from_input(data1.get('tag_id')),
            level=data1.get('level'),
            datetime_created=datetime.now().timestamp()
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
            sample_answer=data1.get('sample_answer'),
            display=data1.get('display'),
            datetime_created=datetime.now().timestamp()
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
            tag_id=get_list_tag_id_from_input(data1.get('tag_id')),
            level=data1.get('level'),
            datetime_created=datetime.now().timestamp()
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            # question_image=data1.get('question_image'),
            # answers=data1.get('answers'),
            # correct_answers=data1.get('correct_answers'),
            sample_answer=data1.get('sample_answer'),
            display=data1.get('display'),
            datetime_created=datetime.now().timestamp()
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#======================DEPRECATED========================
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
    tags=['questions'],
    deprecated=True
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
            datetime_created=datetime.now().timestamp()
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
#=====================DELETE_QUESTIONS===================
#========================================================
@app.delete(
    path='/delete_questions',
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
async def delete_questions(
    data: DATA_Delete_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        all_id = []
        # find question
        for question_id in data.list_question_ids:
            question_del = questions_db[QUESTIONS].find_one_and_update(
                {
                    "_id": ObjectId(question_id),
                    'user_id': data2.get('user_id')       
                },
                {
                    '$set': {
                        'is_removed': True
                    }
                }
            )

            if question_del:
                all_id.append(question_id)
        
                # # find question version
                # question_version = questions_db[QUESTIONS_VERSION].delete_many(
                #     {
                #         'question_id': question_id
                #     }
                # )

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


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
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(question_id),
                    'is_removed': False
                }
            },
            {
                '$set': {
                    'question_id': {
                        '$toString': '$_id'
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
                    'class_id': 1,
                    'subject_id': 1,
                    'chapter_id': 1,
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
            }
        ]
        question_info = questions_db[QUESTIONS].aggregate(pipeline)
        if question_info.alive:
            question_data = question_info.next()
            return JSONResponse(content={'status': 'success', 'data': question_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'question not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===================QUESTION_MORE_DETAIL=================
#========================================================
@app.get(
    path='/question_more_detail/{question_id}',
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
async def question_more_detail(
    question_id: str = Path(..., description='ID of question'),
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(question_id),
                    'is_removed': False
                }
            },
            {
                '$set': {
                    'question_id': {
                        '$toString': '$_id'
                    }
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
                '$set': {
                    'author_info': {
                        '$ifNull': [{'$first': '$author_data'}, None]
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'likes',
                    'localField': 'question_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.QUESTION
                            }
                        }
                    ],
                    'as': 'likes_data'
                }
            },
            {
                '$set': {
                    'num_likes': {
                        '$size': '$likes_data'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'likes',
                    'localField': 'question_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.QUESTION,
                                'user_id': data2.get('user_id')
                            }
                        }
                    ],
                    'as': 'user_like'
                }
            },
            {
                '$set': {
                    'is_liked': {
                        '$ne': ['$user_like', []]
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'comments',
                    'localField': 'question_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.QUESTION,
                                'is_removed': False
                            }
                        }
                    ],
                    'as': 'comments_data'
                }
            },
            {
                '$set': {
                    'num_comments': {
                        '$size': '$comments_data'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'questions_version',
                    'localField': 'question_id',
                    'foreignField': 'question_id',
                    'pipeline': [
                        {
                            '$project' : {
                                '_id': 0,
                                'version_id': {
                                    '$toString': '$_id'
                                },
                                # 'question_id': 1,
                                'version_name': 1
                            }
                        }
                    ],
                    'as': 'question_version'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'question_id': 1,
                    'author_info': 1,
                    'num_comments': 1,
                    'num_likes': 1,
                    'is_liked': 1,
                    'question_version': 1,
                }
            }
        ]
        question_info = questions_db[QUESTIONS].aggregate(pipeline)
        if question_info.alive:
            question_data = question_info.next()
            return JSONResponse(content={'status': 'success', 'data': question_data},status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'question not found!'}, status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=================GET_QUESTION_BY_VERSION================
#========================================================
@app.get(
    path='/get_question_by_version',
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
async def get_question_by_version(
    version_id: str = Query(..., description='question version'),
    data2: dict = Depends(valid_headers)
):
    try:

        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(version_id)
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
                                'is_removed': False
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
                '$project': {
                    '_id': 0,
                    'question_id': 1,
                    'question_version_id': {
                        '$toString': '$_id'
                    },
                    'version_name': 1,
                    "question_content": 1,
                    'level': "$question_information.level",
                    'question_type': "$question_information.type",
                    'tags_info': "$question_information.tags_info",
                    'answers': 1,
                    'answers_right': 1,
                    'sample_answer': 1,
                    'display': 1,
                    'datetime_created': "$question_information.datetime_created"
                }
            }
        ]

        question_data = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        if question_data.alive:
            result_data = question_data.next()
        else:
            msg = 'question not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#========================UPDATE_QUESTION==================
#========================================================
@app.put(
    path='/update_question',
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
async def update_question(
    data1: DATA_Update_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        data1 = jsonable_encoder(data1)
        query_question = {}
        if data1.get('class_id'):
            query_class = {
                'class_id': data1.get('class_id')
            }
            query_question.update(query_class)
        if data1.get('subject_id'):
            query_subject = {
                'subject_id': data1.get('subject_id')
            }
            query_question.update(query_subject)
        if data1.get('chapter_id'):
            query_chapter = {
                'chapter_id': data1.get('chapter_id')
            }
            query_question.update(query_chapter)
        if data1.get('tag_id'):
            query_tag = {
                'tag_id': get_list_tag_id_from_input(data1.get('tag_id'))
            }
            query_question.update(query_tag)
        if data1.get('level'):
            query_level = {
                'level': data1.get('level')
            }
            query_question.update(query_level)
        query_question.update(
            {
                'datetime_updated': datetime.now().timestamp()
            }
        )

        # update question collection
        update_question = questions_db[QUESTIONS].find_one_and_update(
            {
                '_id': ObjectId(data1.get('question_id')),
                'user_id': data2.get('user_id')
            },
            {
                '$set': query_question
            }
        )
        if not update_question:
            msg = 'not your question!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


        # find last version of question
        question_version_info = questions_db[QUESTIONS_VERSION].find_one({
            'question_id': data1.get('question_id'),
            'is_latest': True
        })
        if not question_version_info:
            msg = 'question version not found!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
        query_question_version = {}
        if data1.get('question_content') != question_version_info.get('question_content'):
            query_question_content = {
                'question_content': data1.get('question_content')
            }
            query_question_version.update(query_question_content)
        if data1.get('answers') != question_version_info.get('answers'):
            query_answers = {
                'answers': data1.get('answers')
            }
            query_question_version.update(query_answers)
        if data1.get('answers_right') != question_version_info.get('answers_right'):
            query_answers_right = {
                'answers_right': data1.get('answers_right')
            }
            query_question_version.update(query_answers_right)
        if data1.get('sample_answer') != question_version_info.get('sample_answer'):
            query_sample_answer = {
                'sample_answer': data1.get('sample_answer')
            }
            query_question_version.update(query_sample_answer)
        if data1.get('display') != question_version_info.get('display'):
            query_display = {
                'display': data1.get('display')
            }
            query_question_version.update(query_display)

        if query_question_version:
            # update older version status
            up_question_version = questions_db[QUESTIONS_VERSION].find_one_and_update({
                'question_id': data1.get('question_id'),
                'is_latest': True
            },
            {
                '$set': {
                    'is_latest': False
                }
            })

            # insert new version
            query_version_name = {
                'version_name': question_version_info.get('version_name') + 1,
                'datetime_created': datetime.now().timestamp()
            }
            query_question_version.update(query_version_name)

            del question_version_info['_id']
            question_version_info.update(query_question_version)
            question_version_info = questions_db[QUESTIONS_VERSION].insert_one(question_version_info)
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#===================QUESTION_STATITIC====================
#========================================================
@app.get(
    path='/question_statitic',
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
async def question_statitic(
    subject_id: str = Query(default=None, description='classify by subject'),
    class_id: str = Query(default=None, description='classify by class'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        if not (subject_id or class_id or chapter_id): # all is null
            pipeline_mid = [
                {
                    '$group': {
                        '_id': '$subject_id',
                        'num_questions': {
                            '$count': {}
                        }
                    }
                },
                {
                    '$set': {
                        'subject_object_id': {
                            '$toObjectId': '$_id'
                        }
                    }
                },
                {
                    '$lookup': {
                        'from': 'subject',
                        'localField': 'subject_object_id',
                        'foreignField': '_id',
                        'pipeline': [
                            {
                                '$project': {
                                    '_id': 0,
                                    'name': 1
                                }
                            }
                        ],
                        'as': 'subject_info'
                    }
                },
                {
                    '$unwind': '$subject_info'
                },
                {
                    '$project': {
                        '_id': 0,
                        'id': '$_id',
                        'name': '$subject_info.name',
                        'num_questions': 1,

                    }
                }
            ]
        elif subject_id and not all([subject_id, class_id]): # only subject
            pipeline_mid = [
                {
                    '$group': {
                        '_id': '$class_id',
                        'num_questions': {
                            '$count': {}
                        }
                    }
                },
                {
                    '$set': {
                        'class_object_id': {
                            '$toObjectId': '$_id'
                        }
                    }
                },
                {
                    '$lookup': {
                        'from': 'class',
                        'localField': 'class_object_id',
                        'foreignField': '_id',
                        'pipeline': [
                            {
                                '$project': {
                                    '_id': 0,
                                    'name': 1
                                }
                            }
                        ],
                        'as': 'class_info'
                    }
                },
                {
                    '$unwind': '$class_info'
                },
                {
                    '$project': {
                        '_id': 0,
                        'id': '$_id',
                        'name': '$class_info.name',
                        'num_questions': 1,

                    }
                }
            ]
        elif all([subject_id, class_id]) and not chapter_id:
            pipeline_mid = [
                {
                    '$group': {
                        '_id': '$chapter_id',
                        'num_questions': {
                            '$count': {}
                        }
                    }
                },
                {
                    '$set': {
                        'chapter_object_id': {
                            '$toObjectId': '$_id'
                        }
                    }
                },
                {
                    '$lookup': {
                        'from': 'chapter',
                        'localField': 'chapter_object_id',
                        'foreignField': '_id',
                        'pipeline': [
                            {
                                '$project': {
                                    '_id': 0,
                                    'name': 1
                                }
                            }
                        ],
                        'as': 'chapter_info'
                    }
                },
                {
                    '$unwind': '$chapter_info'
                },
                {
                    '$project': {
                        '_id': 0,
                        'id': '$_id',
                        'name': '$chapter_info.name',
                        'num_questions': 1,

                    }
                }
            ]
        
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(question_id),
                    'is_removed': False
                }
            },
            {
                '$set': {
                    'question_id': {
                        '$toString': '$_id'
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
                    'class_id': 1,
                    'subject_id': 1,
                    'chapter_id': 1,
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
            }
        ]
        question_info = questions_db[QUESTIONS].aggregate(pipeline)
        if question_info.alive:
            question_data = question_info.next()
            return JSONResponse(content={'status': 'success', 'data': question_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'question not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)




