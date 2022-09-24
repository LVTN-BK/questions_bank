from app.utils._header import valid_headers
from app.utils.exam_utils.exam_check_permission import check_permission_view_exam
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_exam
from app.utils.question_utils.question import get_data_and_metadata
from bson import ObjectId
from configs.logger import logger
from configs.settings import EXAMS, EXAMS_CONFIG, EXAMS_EVALUATION, EXAMS_VERSION, GROUP_EXAMS, app, exams_db, group_db
from fastapi import Depends, Path, Query, status
from starlette.responses import JSONResponse
from models.define.target import ManageTargetType

from models.response.exam import UserGetAllExamResponse200, UserGetAllExamResponse403, UserGetOneExamResponse200, UserGetOneExamResponse403



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
    tags=['exams - get']
)
async def user_get_one_exam(
    exam_id: str = Path(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        # if not check_permission_view_exam(exam_id=exam_id, user_id=data2.get('user_id')):
        #     raise Exception('user not have permission to view exam!')

        pipeline = [
            {
                '$match': {
                    "$and": [
                        {
                            '_id': ObjectId(exam_id)
                        },
                        # {
                        #     'user_id': {
                        #         '$eq': data2.get('user_id')
                        #     }
                        # },
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
                        {
                            '$lookup': {
                                'from': 'exams_section',
                                'let': {
                                    'section_id': '$questions'
                                },
                                'pipeline': [
                                    {
                                        '$addFields': {
                                            'section_id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$section_id', '$$section_id']
                                            }
                                        }
                                    },
                                    {
                                        '$unwind': '$section_questions'
                                    },

                                    # join with questions_version
                                    {
                                        '$lookup': {
                                            'from': 'questions_version',
                                            'let': {
                                                'section_question': '$section_questions'
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
                                                            '$eq': ['$question_version_id', '$$section_question']
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
                                                # join with questions db and get question type
                                                {
                                                    "$lookup": {
                                                        'from': 'questions',
                                                        'localField': 'question_object_id',
                                                        'foreignField': '_id',
                                                        # 'let': {
                                                        #     'question_id': '$question_id'
                                                        # },
                                                        'pipeline': [
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
                                                    '$project': {
                                                        '_id': 0,
                                                        'question_id': 1,
                                                        'question_version_id': {
                                                            '$toString': '$_id'
                                                        },
                                                        'version_name': 1,
                                                        "question_content": 1,
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
                                                }
                                            ],
                                            'as': 'section_questions'
                                        }
                                    },
                                    {
                                        '$unwind': '$section_questions'
                                    },
                                    {
                                        '$group': {
                                            '_id': None,
                                            'section_name': {
                                                '$first': '$section_name'
                                            },
                                            'section_questions': {
                                                '$push': '$section_questions'
                                            }
                                        }
                                    },
                                    {
                                        '$project': {
                                            '_id': 0
                                        }
                                    }
                                ],
                                'as': 'questions'
                            }
                        },
                        {
                            '$unwind': '$questions'
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
                                'exam_code': {
                                    '$first': '$exam_code'
                                },
                                'version_name': {
                                    '$first': '$version_name'
                                },
                                'note': {
                                    '$first': '$note'
                                },
                                'time_limit': {
                                    '$first': '$time_limit'
                                },
                                'organization_info': {
                                    '$first': '$organization_info'
                                },
                                'exam_info': {
                                    '$first': '$exam_info'
                                },
                                'questions': {
                                    '$push': '$questions'
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'exam_version_id': '$_id',
                                'version_name': 1,
                                'exam_title': 1,
                                'exam_code': 1,
                                'note': 1,
                                'time_limit': 1,
                                'organization_info': 1,
                                'exam_info': 1,
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
                '$lookup': {
                    'from': 'community_exams',
                    'let': {
                        'exam_id': '$exam_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$exam_id', '$$exam_id']
                                }
                            }
                        }
                    ],
                    'as': 'community_exam_info'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'exam_id': 1,
                    'is_public': {
                        '$ne': ['$community_exam_info', []]
                    },
                    'user_info': {
                        '$ifNull': [{'$first': '$author_data'}, None]
                    },
                    'subject_info': {
                        '$ifNull': [{'$first': '$subject_info'}, None]
                    },
                    'class_info': {
                        '$ifNull': [{'$first': '$class_info'}, None]
                    },
                    'tags_info': 1,
                    'exam_title': '$exam_detail.exam_title',
                    'exam_code': '$exam_detail.exam_code',
                    'exam_version_id': '$exam_detail.exam_version_id',
                    'version_name': '$exam_detail.version_name',
                    'note': '$exam_detail.note',
                    'time_limit': '$exam_detail.time_limit',
                    'organization_info': {
                        '$ifNull': ['$exam_detail.organization_info', None]
                    },
                    'exam_info': {
                        '$ifNull': ['$exam_detail.exam_info', None]
                    },
                    'questions': '$exam_detail.questions',
                    'datetime_created': 1
                    # 'exam_detail': 1
                }
            }
        ]

        # find exam
        exam = exams_db[EXAMS].aggregate(pipeline)
        if exam.alive:
            exam_data = exam.next()
            return JSONResponse(content={'status': 'success', 'data': exam_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'exam not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=====================EXAM_MORE_DETAIL===================
#========================================================
@app.get(
    path='/exam_more_detail/{exam_id}',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - get']
)
async def exam_more_detail(
    exam_id: str = Path(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(exam_id),
                    'is_removed': False
                }
            },
            {
                '$set': {
                    'exam_id': {
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
                    'localField': 'exam_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.EXAM
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
                    'localField': 'exam_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.EXAM,
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
                    'localField': 'exam_id',
                    'foreignField': 'target_id',
                    'pipeline': [
                        {
                            '$match': {
                                'target_type': ManageTargetType.EXAM,
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
                    'from': 'exams_version',
                    'localField': 'exam_id',
                    'foreignField': 'exam_id',
                    'pipeline': [
                        {
                            '$project' : {
                                '_id': 0,
                                'version_id': {
                                    '$toString': '$_id'
                                },
                                # 'exam_id': 1,
                                'version_name': 1
                            }
                        }
                    ],
                    'as': 'exam_version'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'exam_id': 1,
                    'author_info': 1,
                    'num_comments': 1,
                    'num_likes': 1,
                    'is_liked': 1,
                    'exam_version': 1,
                }
            }
        ]
        exam_info = exams_db[EXAMS].aggregate(pipeline)
        if exam_info.alive:
            exam_data = exam_info.next()
            return JSONResponse(content={'status': 'success', 'data': exam_data},status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={'status': 'exam not found!'}, status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================GET_EXAM_BY_VERSION=================
#========================================================
@app.get(
    path='/get_exam_by_version',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetAllExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetAllExamResponse403
        }
    },
    tags=['exams - get']
)
async def get_exam_by_version(
    version_id: str = Query(..., description='ID of exam question'),
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
                '$unwind': '$questions'
            },
            {
                '$lookup': {
                    'from': 'exams_section',
                    'let': {
                        'section_id': '$questions'
                    },
                    'pipeline': [
                        {
                            '$addFields': {
                                'section_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$section_id', '$$section_id']
                                }
                            }
                        },
                        {
                            '$unwind': '$section_questions'
                        },

                        # join with questions_version
                        {
                            '$lookup': {
                                'from': 'questions_version',
                                'let': {
                                    'section_question': '$section_questions'
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
                                                '$eq': ['$question_version_id', '$$section_question']
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
                                    # join with questions db and get question type
                                    {
                                        "$lookup": {
                                            'from': 'questions',
                                            'localField': 'question_object_id',
                                            'foreignField': '_id',
                                            # 'let': {
                                            #     'question_id': '$question_id'
                                            # },
                                            'pipeline': [
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
                                        '$project': {
                                            '_id': 0,
                                            'question_id': 1,
                                            'question_version_id': {
                                                '$toString': '$_id'
                                            },
                                            'version_name': 1,
                                            "question_content": 1,
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
                                    }
                                ],
                                'as': 'section_questions'
                            }
                        },
                        {
                            '$unwind': '$section_questions'
                        },
                        {
                            '$group': {
                                '_id': None,
                                'section_name': {
                                    '$first': '$section_name'
                                },
                                'section_questions': {
                                    '$push': '$section_questions'
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0
                            }
                        }
                    ],
                    'as': 'questions'
                }
            },
            {
                '$unwind': '$questions'
            },
            {
                '$group': {
                    '_id': {
                        '$toString': '$_id',
                    },
                    'exam_id': {
                        '$first': '$exam_id'
                    },
                    'exam_title': {
                        '$first': '$exam_title'
                    },
                    'exam_code': {
                        '$first': '$exam_code'
                    },
                    'version_name': {
                        '$first': '$version_name'
                    },
                    'note': {
                        '$first': '$note'
                    },
                    'time_limit': {
                        '$first': '$time_limit'
                    },
                    'organization_info': {
                        '$first': '$organization_info'
                    },
                    'exam_info': {
                        '$first': '$exam_info'
                    },
                    'questions': {
                        '$push': '$questions'
                    },
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'exam_id': 1,
                    'exam_version_id': '$_id',
                    'version_name': 1,
                    'exam_title': 1,
                    'exam_code': 1,
                    'note': 1,
                    'time_limit': 1,
                    'organization_info': 1,
                    'exam_info': 1,
                    'questions': 1
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
                                'is_removed': False
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
                                'exam_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'community_exams',
                                'let': {
                                    'exam_id': '$exam_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$exam_id', '$$exam_id']
                                            }
                                        }
                                    }
                                ],
                                'as': 'community_exam_info'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'is_public': {
                                    '$ne': ['$community_exam_info', []]
                                },
                                # 'exam_id': 1,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'subject_info': {
                                    '$ifNull': [{'$first': '$subject_info'}, None]
                                },
                                'class_info': {
                                    '$ifNull': [{'$first': '$class_info'}, None]
                                },
                                'tags_info': 1,
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
                '$project': {
                    '_id': 0,
                    'exam_id': 1,
                    'is_public': '$exam_detail.is_public',
                    'user_info': '$exam_detail.user_info',
                    'class_info': '$exam_detail.class_info',
                    'subject_info': '$exam_detail.subject_info',
                    'tags_info': '$exam_detail.tags_info',
                    'exam_title': 1,
                    'exam_code': 1,
                    'exam_version_id': 1,
                    'version_name': 1,
                    'note': 1,
                    'time_limit': 1,
                    'organization_info': {
                        '$ifNull': ['$organization_info', None]
                    },
                    'exam_info': {
                        '$ifNull': ['$exam_info', None]
                    },
                    'questions': 1,
                    'datetime_created': '$exam_detail.datetime_created'
                }
            }
        ]

        exam_data = exams_db[EXAMS_VERSION].aggregate(pipeline)
        if exam_data.alive:
            result_data = exam_data.next()
        else:
            msg = 'exam not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================GROUP_GET_ONE_EXAM==================
#========================================================
@app.get(
    path='/group/get_one_exam/{exam_id}',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetOneExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetOneExamResponse403
        }
    },
    tags=['exams - get'],
    deprecated=True
)
async def group_get_one_exam(
    exam_id: str = Path(..., description='ID of exam'),
    group_id: str = Path(..., description='ID of group'),
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

        # check group has exam with exam_id
        query_check = {
            'exam_id': exam_id,
            'group_id': group_id
        }
        exam_check = group_db[GROUP_EXAMS].find_one(query_check)
        if not exam_check:
            return JSONResponse(content={'status': 'Not Found'}, status_code=status.HTTP_404_NOT_FOUND)

        pipeline = [
            {
                '$match': {
                    "$and": [
                        {
                            '_id': ObjectId(exam_id)
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
                                    {
                                        '$addFields': { # convert question_id in questions_version collection from string to ObjectId(to join with questions collection)
                                            'question_object_id': {
                                                '$toObjectId': '$question_id'
                                            }
                                        }
                                    },
                                    # join with questions db and get question type
                                    {
                                        "$lookup": {
                                            'from': 'questions',
                                            'localField': 'question_object_id',
                                            'foreignField': '_id',
                                            # 'let': {
                                            #     'question_id': '$question_id'
                                            # },
                                            'pipeline': [
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
                                'version_name': {
                                    '$first': '$version_name'
                                },
                                'note': {
                                    '$first': '$note'
                                },
                                'time_limit': {
                                    '$first': '$time_limit'
                                },
                                'organization_info': {
                                    '$first': '$organization_info'
                                },
                                'exam_info': {
                                    '$first': '$exam_info'
                                },
                                'questions': {
                                    '$push': '$questions'
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'exam_version_id': '$_id',
                                'version_name': 1,
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'organization_info': 1,
                                'exam_info': 1,
                                'questions': 1
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
                    'exam_version_id': '$exam_detail.exam_version_id',
                    'version_name': '$exam_detail.version_name',
                    'note': '$exam_detail.note',
                    'time_limit': '$exam_detail.time_limit',
                    'organization_info': {
                        '$ifNull': ['$exam_detail.organization_info', None]
                    },
                    'exam_info': {
                        '$ifNull': ['$exam_detail.exam_info', None]
                    },
                    'questions': '$exam_detail.questions',
                    'datetime_created': 1
                    # 'exam_detail': 1
                }
            }
        ]

        # find exam
        exam = exams_db[EXAMS].aggregate(pipeline)

        if exam.alive:
            data = exam.next()
        else:
            msg = 'exam not found'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # for section_idx, section in enumerate(data['questions']):
        #     for question_idx, question in enumerate(data['questions'][section_idx]['section_questions']):
        #         question_type = data['questions'][section_idx]['section_questions'][question_idx]['question_type']
        #         answers = data['questions'][section_idx]['section_questions'][question_idx]['answers']
        #         data['questions'][section_idx]['section_questions'][question_idx]['answers'] = get_answer(answers=answers, question_type=question_type)
 
        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=================COMMUNITY_GET_ONE_EXAM=================
#========================================================
@app.get(
    path='/community/get_one_exam/{exam_id}',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetOneExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetOneExamResponse403
        }
    },
    tags=['exams - get'],
    deprecated=True
)
async def community_get_one_exam(
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
                            'is_public': True
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
    tags=['exams - get']
)
async def user_get_all_exam(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: str = Query(default=None, description='text search'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        # find exam
        filter_exam = [{}]
        filter_exam_version = [{}]

        # =============== search =================
        if search:
            query_search = {
                'exam_title': {
                    '$regex': search,
                    '$options': 'i'
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
                                'exam_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'community_exams',
                                'let': {
                                    'exam_id': '$exam_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$exam_id', '$$exam_id']
                                            }
                                        }
                                    }
                                ],
                                'as': 'community_exam_info'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                # 'exam_id': 1,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'subject_info': {
                                    '$ifNull': [{'$first': '$subject_info'}, None]
                                },
                                'class_info': {
                                    '$ifNull': [{'$first': '$class_info'}, None]
                                },
                                'tags_info': 1,
                                'is_public': {
                                    '$ne': ['$community_exam_info', []]
                                },
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
                                'exam_id': 1,
                                'user_info': '$exam_detail.user_info',
                                'class_info': '$exam_detail.class_info',
                                'subject_info': '$exam_detail.subject_info',
                                'tags_info': '$exam_detail.tags_info',
                                'is_public': '$exam_detail.is_public',
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'organization_info': {
                                    '$ifNull': ['$organization_info', None]
                                },
                                'exam_info': {
                                    '$ifNull': ['$exam_info', None]
                                },
                                # 'questions': 1,
                                'datetime_created': '$exam_detail.datetime_created'
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
            }
        ]

        exams = exams_db[EXAMS_VERSION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=exams, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================GROUP_GET_ALL_EXAM==================
#========================================================
@app.get(
    path='/group/get_all_exam',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetAllExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetAllExamResponse403
        }
    },
    tags=['exams - get']
)
async def group_get_all_exam(
    group_id: str = Query(..., description='ID of group'),
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: str = Query(default=None, description='text search'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    # chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
        # find exam
        filter_exam = [{}]
        filter_exam_version = [{}]

        #check group exist:
        if not check_group_exist(group_id=group_id):
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # check owner of group or member
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=group_id):
            content = {'status': 'failed', 'msg': 'User is not the owner or member of group'}
            return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)


        # get list exam of group
        list_exam = get_list_group_exam(group_id=group_id)
        # =============== list_group_exam =================
        query_exam = {
            'exam_id': {
                '$in': list_exam
            }
        }
        filter_exam_version.append(query_exam)


        # =============== search =================
        if search:
            query_search = {
                'exam_title': {
                    '$regex': search,
                    '$options': 'i'
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

        # # =============== owner =================
        # query_exam_owner = {
        #     'user_id': {
        #         '$eq': data2.get('user_id')
        #     }
        # }
        # filter_exam.append(query_exam_owner)

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

        # # =============== chapter =================
        # if chapter_id:
        #     query_exam_chapter = {
        #         'chapter_id': chapter_id
        #     }
        #     filter_exam.append(query_exam_chapter)

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
                            '$addFields': {
                                'exam_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        # {
                        #     '$match': {
                        #         "$expr": {
                        #             '$in': ['$exam_id', list_exam]
                        #         }
                        #     }
                        # },
                        {
                            '$lookup': {
                                'from': 'group_exams',
                                'let': {
                                    'exam_id': '$exam_id'
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
                                                        '$eq': ['$exam_id', '$$exam_id']
                                                    }
                                                },
                                            ]
                                        }
                                    }
                                ],
                                'as': 'group_exam_info'
                            }
                        },
                        {
                            '$unwind': "$group_exam_info"
                        },
                        {
                            '$set': {
                                'subject_id': '$group_exam_info.subject_id',
                                'class_id': '$group_exam_info.class_id',
                                'datetime_shared': '$group_exam_info.datetime_created',
                            }
                        },
                        {
                            '$match': {
                                '$and': filter_exam
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
                            '$project': {
                                '_id': 0,
                                # 'exam_id': 1,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'subject_info': {
                                    '$ifNull': [{'$first': '$subject_info'}, None]
                                },
                                'class_info': {
                                    '$ifNull': [{'$first': '$class_info'}, None]
                                },
                                'tags_info': 1,
                                'datetime_shared': 1,
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
                                'exam_id': 1,
                                'exam_version_id': {
                                    '$toString': '$_id'
                                },
                                'user_info': '$exam_detail.user_info',
                                'class_info': '$exam_detail.class_info',
                                'subject_info': '$exam_detail.subject_info',
                                'tags_info': '$exam_detail.tags_info',
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'organization_info': {
                                    '$ifNull': ['$organization_info', None]
                                },
                                'exam_info': {
                                    '$ifNull': ['$exam_info', None]
                                },
                                'datetime_shared': '$exam_detail.datetime_shared',
                                'datetime_created': '$exam_detail.datetime_created'
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
            }
        ]

        exams = exams_db[EXAMS_VERSION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=exams, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#==================COMMUNITY_GET_ALL_EXAM================
#========================================================
@app.get(
    path='/community/get_all_exam',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetAllExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetAllExamResponse403
        }
    },
    tags=['exams - get']
)
async def community_get_all_exam(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    search: str = Query(default=None, description='text search'),
    class_id: str = Query(default=None, description='classify by class'),
    subject_id: str = Query(default=None, description='classify by subject'),
    # chapter_id: str = Query(default=None, description='classify by chapter'),
    data2: dict = Depends(valid_headers)
):
    try:
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

        # # =============== public =================
        # query_exam_public = {
        #     'is_public': {
        #         '$eq': True
        #     }
        # }
        # filter_exam.append(query_exam_public)

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

        # # =============== chapter =================
        # if chapter_id:
        #     query_exam_chapter = {
        #         'chapter_id': chapter_id
        #     }
        #     filter_exam.append(query_exam_chapter)

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
                            '$addFields': {
                                'exam_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'community_exams',
                                'let': {
                                    'exam_id': '$exam_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$exam_id', '$$exam_id']
                                            }
                                        }
                                    }
                                ],
                                'as': 'community_exam_info'
                            }
                        },
                        {
                            '$unwind': "$community_exam_info"
                        },
                        {
                            '$set': {
                                'subject_id': '$community_exam_info.subject_id',
                                'class_id': '$community_exam_info.class_id',
                                'datetime_shared': '$community_exam_info.datetime_created',
                            }
                        },
                        {
                            '$match': {
                                '$and': filter_exam
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
                            '$project': {
                                '_id': 0,
                                # 'exam_id': 1,
                                'user_info': {
                                    '$ifNull': [{'$first': '$author_data'}, None]
                                },
                                'subject_info': {
                                    '$ifNull': [{'$first': '$subject_info'}, None]
                                },
                                'class_info': {
                                    '$ifNull': [{'$first': '$class_info'}, None]
                                },
                                'tags_info': 1,
                                'datetime_shared': 1,
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
                                'exam_id': 1,
                                'exam_version_id': {
                                    '$toString': '$_id'
                                },
                                'user_info': '$exam_detail.user_info',
                                'class_info': '$exam_detail.class_info',
                                'subject_info': '$exam_detail.subject_info',
                                'tags_info': '$exam_detail.tags_info',
                                'exam_title': 1,
                                'note': 1,
                                'time_limit': 1,
                                'organization_info': {
                                    '$ifNull': ['$organization_info', None]
                                },
                                'exam_info': {
                                    '$ifNull': ['$exam_info', None]
                                },
                                'datetime_shared': '$exam_detail.datetime_shared',
                                'datetime_created': '$exam_detail.datetime_created'
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
            }
        ]

        exams = exams_db[EXAMS_VERSION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=exams, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===================GET_EXAM_EVALUATION==================
#========================================================
@app.get(
    path='/get_exam_evaluation',
    responses={
        status.HTTP_200_OK: {
            'model': UserGetAllExamResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': UserGetAllExamResponse403
        }
    },
    tags=['exams - get']
)
async def get_exam_evaluation(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    exam_id: str = Query(..., description='ID of exam'),
    data2: dict = Depends(valid_headers)
):
    try:
        num_skip = (page - 1)*limit

        pipeline = [
            {
                '$match': {
                    "exam_id": exam_id,
                    'user_id': data2.get('user_id')
                }
            },
            {
                '$set': {
                    'eval_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'questions_evaluation',
                    'let': {
                        'eval_id': '$eval_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$evaluation_id', '$$eval_id']
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'questions',
                                'let': {
                                    'question_id': '$question_id'
                                },
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
                                            '$expr': {
                                                '$eq': ['$question_id', '$$question_id']
                                            }
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
                                'is_owner': {
                                    '$eq': ['$question_info.user_id', data2.get('user_id')]
                                }
                            }
                        },
                        {
                            '$sort': {
                                'datetime_created': 1
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'user_id': 0,
                                'evaluation_id': 0,
                                'datetime_created': 0,
                                'question_info': 0
                            }
                        }
                    ],
                    'as': 'data'
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
                                'exam_id': 1,
                                'datetime_created': 1,
                                'data': 1
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
            }
        ]

        exams = exams_db[EXAMS_EVALUATION].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=exams, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#====================USER_EXAM_STATISTIC=================
#========================================================
@app.get(
    path='/user_exam_statistic',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - get']
)
async def user_exam_statistic(
    subject_id: str = Query(default=None, description='classify by subject'),
    class_id: str = Query(default=None, description='classify by class'),
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline_head = {
            'user_id': data2.get('user_id'),
            'is_removed': False
        }
    
        body_facet = {
            'total_exam': [
                {
                    '$count': 'count'
                }
            ]
        }
        if not (subject_id or class_id): # all is null
            pipeline_mid = [
                {
                    '$group': {
                        '_id': '$subject_id',
                        'num_exams': {
                            '$count': {}
                        }
                    }
                },
                # {
                #     '$set': {
                #         'subject_object_id': {
                #             '$toObjectId': '$_id'
                #         }
                #     }
                # },
                {
                    '$lookup': {
                        'from': 'subject',
                        # 'localField': 'subject_object_id',
                        # 'foreignField': '_id',
                        'let': {
                            'subject_id': '$_id'
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
                        'num_exams': 1,

                    }
                }
            ]
            body_facet['subjects'] = pipeline_mid

        elif subject_id and not class_id: # only subject
            pipeline_mid = [
                {
                    '$group': {
                        '_id': '$class_id',
                        'num_exams': {
                            '$count': {}
                        }
                    }
                },
                # {
                #     '$set': {
                #         'class_object_id': {
                #             '$toObjectId': '$_id'
                #         }
                #     }
                # },
                {
                    '$lookup': {
                        'from': 'class',
                        # 'localField': 'class_object_id',
                        # 'foreignField': '_id',
                        'let': {
                            'class_id': '$_id'
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
                        'num_exams': 1,

                    }
                }
            ]
            body_facet['classes'] = pipeline_mid

            pipeline_head.update(
                {
                    'subject_id': subject_id
                }
            )
        
        elif all([subject_id, class_id]):
            pipeline_head.update(
                {
                    'subject_id': subject_id,
                    'class_id': class_id
                }
            )

        pipeline_facet = [
            {
                '$facet': body_facet
            },
            {
                '$unwind': '$total_exam'
            },
            {
                '$set': {
                    'total_exam': '$total_exam.count'
                }
            }
        ]

        pipeline_match = [
            {
                '$match': pipeline_head
            }
        ]

        pipeline = pipeline_match + pipeline_facet
        
        exam_info = exams_db[EXAMS].aggregate(pipeline)
        exam_data = {}
        if exam_info.alive:
            exam_data = exam_info.next()

        return JSONResponse(content={'status': 'success', 'data': exam_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#====================USER_GET_EXAM_CONFIG================
#========================================================
@app.get(
    path='/user_get_exam_config',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - get']
)
async def user_get_exam_config(
    page: int = Query(default=1, description='page number'),
    limit: int = Query(default=10, description='limit of num result'),
    data2: dict = Depends(valid_headers)
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
                                'name': 1,
                                'data': 1,
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
            }
        ]

        exams = exams_db[EXAMS_CONFIG].aggregate(pipeline)
        
        result_data, meta_data = get_data_and_metadata(aggregate_response=exams, page=page)

        return JSONResponse(content={'status': 'success', 'data': result_data, 'metadata': meta_data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)



