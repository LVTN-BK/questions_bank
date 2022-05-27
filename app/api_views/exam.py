from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.question_utils.question import get_answer, get_question_information_with_version_id
from bson import ObjectId
from configs.logger import logger
from configs.settings import EXAMS, EXAMS_VERSION, SYSTEM, app, exams_db
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.exam import Exams_DB, Exams_Version_DB
from models.request.exam import DATA_Create_Exam
from starlette.responses import JSONResponse

from models.response.exam import UserGetAllExamResponse200, UserGetAllExamResponse403, UserGetOneExamResponse200, UserGetOneExamResponse403


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
            'model': UserGetOneExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetOneExamResponse403
        }
    },
    tags=['exams']
)
async def user_get_one_exam(
    exam_id: str = Path(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        start_time = datetime.now()
        

        pipeline_v1 = [
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
                            '$project': {
                                '_id': 0,
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'questions': 1
                            }
                        },
                        # {
                        #     '$unwind': '$exam_title'
                        # },
                    ],
                    'as': 'exam_detail'
                }
            },
            {
                '$unwind': '$exam_detail'
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

            #join with exam_version
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

                        # join with questions_version
                        {
                            '$lookup': {
                                'from': 'questions_version',
                                'let': {
                                    'section_question': '$questions.section_questions'
                                },
                                'pipeline': [
                                    {
                                        '$addFields': {
                                            'question_version_id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$in': ['$question_version_id', '$$section_question']
                                            }
                                        }
                                    },
                                    # join with questions db and get question type
                                    {
                                        "$lookup": {
                                            'from': 'questions',
                                            'let': {
                                                'question_id': '$question_id'
                                            },
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
                                                        '$expr': {
                                                            '$eq': ['$question_id', '$$question_id']
                                                        }
                                                    }
                                                },
                                                {
                                                    '$project': {
                                                        '_id': 0,
                                                        'question_type': '$type',
                                                    }
                                                }
                                            ],
                                            'as': 'question_info'
                                        }
                                    },
                                    {
                                        '$unwind': '$question_info'
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

                                    # continue join with answers to get answers_right(matching question)
                                    {
                                        '$lookup': {
                                            'from': 'answers',
                                            'let': {
                                                'list_answers': '$answers_right'
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
                                            'as': 'answers_right'
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
                                            'question_type': '$question_info.question_type',
                                            'answers': 1,
                                            'answers_right': 1,
                                            'correct_answers': 1,
                                            'datetime_created': 1
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
                            '$project': {
                                '_id': 0,
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'questions': 1
                            }
                        },
                        # {
                        #     '$unwind': '$exam_title'
                        # },
                    ],
                    'as': 'exam_detail'
                }
            },
            {
                '$unwind': '$exam_detail'
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
                    'questions': '$exam_detail.questions',
                    'datetime_created': 1
                    # 'exam_detail': 1
                }
            }
        ]

        # find exam
        exam = exams_db[EXAMS].aggregate(pipeline)

        logger().info(f'type exam: {type(exam)}')
        data = exam.next()

        # for section_idx, section in enumerate(data['questions']):
        #     for question_idx, question in enumerate(data['questions'][section_idx]['section_questions']):
        #         question_type = data['questions'][section_idx]['section_questions'][question_idx]['question_type']
        #         answers = data['questions'][section_idx]['section_questions'][question_idx]['answers']
        #         data['questions'][section_idx]['section_questions'][question_idx]['answers'] = get_answer(answers=answers, question_type=question_type)
 
        end_time = datetime.now()
        logger().info(end_time-start_time)
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
            'model': UserGetAllExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetAllExamResponse403
        }
    },
    tags=['exams']
)
async def user_get_all_exam(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: Optional[str] = Query(default=None, description='text search'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        result = []
        # find exam
        filter_exam = [{}]
        filter_exam_version = [{}]

        # =============== search =================
        if search:
            query_search = {
                '$text': {
                    '$search': search
                }
            }
            filter_exam_version.append(query_search)
        
        # =============== version =================
        query_latest_version = {
            'is_latest': True
        }
        filter_exam_version.append(query_latest_version)

        # =============== status =================
        query_exam_status = {
            'is_removed': False
        }
        filter_exam.append(query_exam_status)

        # =============== owner =================
        query_exam_owner = {
            'user_id': {
                '$eq': data2.get('user_id')
            }
        }
        filter_exam.append(query_exam_owner)

        # =============== class =================
        if class_id:
            query_exam_class = {
                'class_id': class_id
            }
            filter_exam.append(query_exam_class)

        # =============== subject =================
        if subject_id:
            query_exam_subject = {
                'subject_id': subject_id
            }
            filter_exam.append(query_exam_subject)

        # =============== chapter =================
        if chapter_id:
            query_exam_chapter = {
                'chapter_id': chapter_id
            }
            filter_exam.append(query_exam_chapter)

        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    "$and": filter_exam_version
                }
            },
            {
                '$addFields': {
                    'exam_object_id': {
                        '$toObjectId': '$exam_id'
                    }
                }
            },

            #join with exam
            {
                "$lookup": {
                    'from': 'exams',
                    'localField': 'exam_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$match': {
                                '$and': filter_exam
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'exam_id': 1,
                                'user_id': 1,
                                'class_id': 1,
                                'subject_id': 1,
                                'tag_id': 1,
                                'datetime_created': 1
                            }
                        },
                    ],
                    'as': 'exam_detail'
                }
            },
            {
                '$unwind': '$exam_detail'
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
                                'exam_id': '$exam_detail.exam_id',
                                'user_id': '$exam_detail.user_id',
                                'class_id': '$exam_detail.class_id',
                                'subject_id': '$exam_detail.subject_id',
                                'tag_id': '$exam_detail.tag_id',
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'questions': 1,
                                'datetime_created': '$exam_detail.datetime_created'
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
            }
        ]

        exams = exams_db[EXAMS_VERSION].aggregate(pipeline)
        
        exams_data = exams.next()

        exams_count = exams_data['metadata']['total']
        num_pages = exams_data.get('metadata').get('page')
        
        meta_data = {
            'count': exams_count,
            'current_page': page,
            'has_next': (num_pages>page),
            'has_previous': (page>1),
            'next_page_number': (page+1) if (num_pages>page) else None,
            'num_pages': num_pages,
            'previous_page_number': (page-1) if (page>1) else None,
            'valid_page': (page>=1) and (page<=num_pages)
        }

        
        # for exam in exams:
        #     result.append(exam)

        # exams = exams_db[EXAMS].find(
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
        
        # for exam in exams:
        #     # find exam version
        #     exam_version = exams_db[EXAMS_VERSION].find_one(
        #         {
        #             '$and': [
        #                 {
        #                     'exam_id': str(exam['_id'])
        #                 },
        #                 {
        #                     'is_latest': True
        #                 }
        #             ]
        #         }
        #     )
        #     if exam_version:
        #         del exam['_id']
        #         del exam_version['_id']
        #         exam['exam_info'] = exam_version
        #         result.append(exam)
        #     else:
        #         del exam['_id']
        #         exam['exam_info'] = {}
        #         result.append(exam)

        return JSONResponse(content={'status': 'success', 'data': exams_data['data'], 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
