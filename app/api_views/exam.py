from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.question_utils.question import \
    get_question_information_with_version_id
from bson import ObjectId
from configs.logger import logger
from configs.settings import EXAMS, EXAMS_VERSION, SYSTEM, app, exams_db
from fastapi import Depends, Path, status
from fastapi.encoders import jsonable_encoder
from models.db.exam import Exams_DB, Exams_Version_DB
from models.request.exam import DATA_Create_Exam
from starlette.responses import JSONResponse


#========================================================
#=====================CREATE_EXAM========================
#========================================================
@app.post(
    path='/create_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams']
)
async def create_exam(
    data1: DATA_Create_Exam,
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
        
        exam = Exams_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            tag_id=data1.get('tag_id'),
        )

        logger().info(f'exam: {exam}')

        # insert to exams table
        id_exam = exams_db[EXAMS].insert_one(jsonable_encoder(exam)).inserted_id

        # insert exam version to exams_version
        exams_version = Exams_Version_DB(
            exam_id=str(id_exam),
            exam_title=data1.get('exam_title'),
            note=data1.get('note'),
            time_limit=data1.get('time_limit'),
            questions=data1.get('questions')
        )
        id_exam_version = exams_db[EXAMS_VERSION].insert_one(jsonable_encoder(exams_version)).inserted_id

        exam = jsonable_encoder(exam)
        exams_version = jsonable_encoder(exams_version)
        exam.update({'exam_info': exams_version})

        return JSONResponse(content={'status': 'success', 'data': exam},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

# #========================================================
# #=====================USER_GET_ONE_EXAM==================
# #========================================================
# @app.get(
#     path='/user/get_one_exam/{exam_id}',
#     responses={
#         status.HTTP_200_OK: {
#             'model': ''
#         },
#         status.HTTP_403_FORBIDDEN: {
#             'model': ''
#         }
#     },
#     tags=['exams']
# )
# async def user_get_one_exam(
#     exam_id: str = Path(..., description='ID of exam'),
#     data2: dict = Depends(valid_headers)
# ):
#     try:
#         # find exam
#         exam = exams_db[EXAMS].find_one(
#             {
#                 "$and": [
#                     {
#                         '_id': ObjectId(exam_id)
#                     },
#                     {
#                         'user_id': {
#                             '$eq': data2.get('user_id')
#                         }
#                     },
#                     {
#                         'is_removed': False
#                     }
#                 ]
                        
#             }
#         )
#         if not exam:
#             return JSONResponse(content={'status': 'Exam not found!'}, status_code=status.HTTP_404_NOT_FOUND)
        
#         # find exam version
#         exam_version = exams_db[EXAMS_VERSION].find_one(
#             {
#                 '$and': [
#                     {
#                         'exam_id': exam_id
#                     },
#                     {
#                         'is_latest': True
#                     }
#                 ]
#             }
#         )
#         if not exam_version:
#             return JSONResponse(content={'status': 'Exam not found!'}, status_code=status.HTTP_404_NOT_FOUND)

#         # get question infomation
#         all_question = []
#         for question in exam_version.get('questions'):
#             question_info = get_question_information_with_version_id(question_version_id=question)
#             all_question.append(question_info)
        
#         exam_version['questions'] = all_question
#         del exam_version['_id']
#         del exam['_id']
#         exam['exam_info'] = exam_version

#         logger().info(exam_version)

#         return JSONResponse(content={'status': 'success', 'data': exam},status_code=status.HTTP_200_OK)
#     except Exception as e:
#         logger().error(e)
#     return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=====================USER_GET_ONE_EXAM==================
#========================================================
@app.get(
    path='/user/get_one_exam/{exam_id}',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams']
)
async def user_get_one_exam(
    exam_id: str = Path(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        

        pipeline = [
            {
                '$match': {
                    "$and": [
                        {
                            '_id': ObjectId(exam_id)
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
            },
            {
                '$addFields': {
                    'exam_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                "$lookup": {
                    'from': 'exams_version',
                    'localField': 'exam_id',
                    'foreignField': 'exam_id',
                    'pipeline': [
                        {
                            '$match': {
                                'is_latest': True
                            }
                        },
                        {
                            '$unwind': '$questions'
                        },
                        {
                            '$lookup': {
                                'from': 'questions',
                                'let': {
                                    'section_question': '$questions.section_questions'
                                },
                                'pipeline': [
                                    {
                                        '$addFields': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$id', '$$section_question']
                                            }
                                        }
                                    },
                                    # join with questions_version
                                    {
                                        '$lookup': {
                                            'from': 'questions_version',
                                            'localField': 'id',
                                            'foreignField': 'question_id',
                                            'pipeline': [
                                                {
                                                    '$match': {
                                                        'is_latest': True
                                                    }
                                                },
                                                # join with answers
                                                {
                                                    '$lookup': {
                                                        'from': 'answers',
                                                        'let': {
                                                            'list_answers': '$answers'
                                                        },
                                                        'pipeline': [
                                                            {
                                                                '$addFields': {
                                                                    'answer_id': {
                                                                        '$toString': '$_id'
                                                                    }
                                                                }
                                                            },
                                                            {
                                                                '$match': {
                                                                    '$expr': {
                                                                        '$in': ['$answer_id', '$$list_answers']
                                                                    }
                                                                }
                                                            },
                                                            {
                                                                '$project': {
                                                                    '_id': 0,
                                                                    'answer_id': 1,
                                                                    'answer_content': 1,
                                                                    'answer_image': 1,
                                                                    'datetime_created': 1
                                                                }
                                                            }
                                                        ],
                                                        'as': 'answers'
                                                    }
                                                },
                                                {
                                                    '$project': {
                                                        '_id': 0,
                                                        'question_version_id': {
                                                            '$toString': '$_id'
                                                        },
                                                        'question_id': 1,
                                                        'question_content': 1,
                                                        'question_image': 1,
                                                        'answers': 1,
                                                        'correct_answers': 1,
                                                        'datetime_created': 1
                                                    }
                                                }
                                            ],
                                            'as': 'question_version'
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'type': 1,
                                            'level': 1,
                                            'question_version': 1
                                        }
                                    }
                                ],
                                'as': 'questions.section_questions'
                            }
                        },
                        {
                            '$group': {
                                '_id': {
                                    '$toString': '$_id'
                                },
                                # 'exam_id': '$exam_id',
                                'exam_title': {
                                    '$first': '$exam_title'
                                },
                                'note': {
                                    '$first': '$note'
                                },
                                'time_limit': {
                                    '$first': '$time_limit'
                                },
                                'questions': {
                                    '$push': '$questions'
                                }
                            }
                        },
                        {
                            '$unwind': '$exam_title'
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'questions': 1
                            }
                        }
                    ],
                    'as': 'exam_detail'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    # 'exam_id': {
                    #     '$toString': '$_id'
                    # },
                    'exam_id': 1,
                    'user_id': 1,
                    'class_id': 1,
                    'subject_id': 1,
                    'tag_id': 1,
                    'exam_title': '$exam_detail.exam_title',
                    'note': '$exam_detail.note',
                    'time_limit': '$exam_detail.time_limit',
                    'questions': '$exam_detail.questions'
                    # 'exam_detail': 1
                }
            }
        ]

        # find exam
        exam = exams_db[EXAMS].aggregate(pipeline)

        logger().info(f'type exam: {type(exam)}')
        data = exam.next()

        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=====================USER_GET_ALL_EXAM==================
#========================================================
@app.get(
    path='/user/get_all_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams']
)
async def user_get_all_exam(
    data2: dict = Depends(valid_headers)
):
    try:
        result = []
        # find exam
        exams = exams_db[EXAMS].find(
            {
                "$and": [
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
        
        for exam in exams:
            # find exam version
            exam_version = exams_db[EXAMS_VERSION].find_one(
                {
                    '$and': [
                        {
                            'exam_id': str(exam['_id'])
                        },
                        {
                            'is_latest': True
                        }
                    ]
                }
            )
            if exam_version:
                del exam['_id']
                del exam_version['_id']
                exam['exam_info'] = exam_version
                result.append(exam)
            else:
                del exam['_id']
                exam['exam_info'] = {}
                result.append(exam)

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
