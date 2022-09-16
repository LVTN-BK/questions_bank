import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_chapter_info, get_class_info, get_subject_info
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from configs.logger import logger
from configs.settings import (ANSWERS, COMMUNITY_QUESTIONS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
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
                    },
                    'question_ids': {
                        '$addToSet': '$_id'
                    }
                }
            },
            {
                '$unwind': '$subject'
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'let': {
                        'subject_id': '$subject'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                '_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$_id','$$subject_id']
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
                '$lookup': {
                    'from': 'questions',
                    'let': {
                        'subject': '$subject',
                        'question_ids': '$question_ids'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$and': [
                                    {
                                        '$expr': {
                                            '$in': ['$_id', '$$question_ids']
                                        }
                                    },
                                    {
                                        '$expr': {
                                            '$eq': ['$subject_id', '$$subject']
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            '$group': {
                                '_id': None,
                                'subject': {
                                    '$first': '$subject_id'
                                },
                                'class': {
                                    '$addToSet': '$class_id'
                                },
                                'question_ids': {
                                    '$addToSet': '$_id'
                                }
                            }
                        },
                        {
                            '$unwind': '$class'
                        },
                        {
                            '$lookup': {
                                'from': 'class',
                                'let': {
                                    'class_id': '$class'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            '_id': {
                                                '$toString': '$_id'
                                            }
                                        }
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$_id','$$class_id']
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
                            '$lookup': {
                                'from': 'questions',
                                'let': {
                                    'class': '$class',
                                    'subject': '$subject',
                                    'question_ids': '$question_ids'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$and': [
                                                {
                                                    '$expr': {
                                                        '$in': ['$_id', '$$question_ids']
                                                    }
                                                },
                                                {
                                                    '$expr': {
                                                        '$eq': ['$subject_id', '$$subject']
                                                    }
                                                },
                                                {
                                                    '$expr': {
                                                        '$eq': ['$class_id', '$$class']
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        '$group': {
                                            '_id': None,
                                            'chapter': {
                                                '$addToSet': '$chapter_id'
                                            },
                                        }
                                    },
                                    {
                                        '$unwind': '$chapter'
                                    },
                                    {
                                        '$lookup': {
                                            'from': 'chapter',
                                            'let': {
                                                'chapter_id': '$chapter'
                                            },
                                            'pipeline': [
                                                {
                                                    '$set': {
                                                        '_id': {
                                                            '$toString': '$_id'
                                                        }
                                                    }
                                                },
                                                {
                                                    '$match': {
                                                        '$expr': {
                                                            '$eq': ['$_id','$$chapter_id']
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
                                            'as': 'chapter_info'
                                        }
                                    },
                                    {
                                        '$unwind': '$chapter_info'
                                    },
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': '$chapter',
                                            'name': '$chapter_info.name'
                                        }
                                    },
                                    {
                                        '$sort': {
                                            'name': 1
                                        }
                                    }
                                ],
                                'as': 'chapters'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': '$class',
                                'name': '$class_info.name',
                                'chapters': 1
                            }
                        },
                        {
                            '$sort': {
                                'name': 1
                            }
                        }
                    ],
                    'as': 'classes'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'id': '$subject',
                    'name': '$subject_info.name',
                    'classes': 1
                }
            },
            {
                '$sort': {
                    'name': 1
                }
            },
            {
                '$group': {
                    '_id': 0,
                    'subjects': {
                        '$push': '$$ROOT'
                    }
                }
            }
        ]

        questions = questions_db[QUESTIONS].aggregate(pipeline)
        
        data_return = []
        if questions.alive:
            questions_data = questions.next()
            logger().info(f'questions_data: {questions_data}')
            data_return=questions_data.get('subjects')
        
        return JSONResponse(content={'status': 'success', 'data': data_return},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



#========================================================
#===============GROUP_GET_QUESTION_CLASSIFY==============
#========================================================
@app.get(
    path='/group/get_question_classify',
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
async def group_get_question_classify(
    group_id: str = Query(..., description='ID of group'),
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

        pipeline = [
            {
                '$match': {
                    'group_id': group_id
                }
            },
            {
                '$group': {
                    '_id': '$subject_id'
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'let': {
                        'subject_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            },
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$subject_id']
                                }
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
                '$lookup': {
                    'from': 'group_questions',
                    'let': {
                        'subject_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                'group_id': group_id,
                                '$expr': {
                                    '$eq': ['$subject_id', '$$subject_id']
                                }
                            }
                        },
                        {
                            '$group': {
                                '_id': '$class_id'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'class',
                                'let': {
                                    'class_id': '$_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        },
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$class_id']
                                            }
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
                            '$lookup': {
                                'from': 'group_questions',
                                'let': {
                                    'class_id': '$_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            'group_id': group_id,
                                            '$expr': {
                                                '$eq': ['$class_id', '$$class_id']
                                            }
                                        }
                                    },
                                    {
                                        '$group': {
                                            '_id': '$chapter_id',
                                        }
                                    },
                                    {
                                        '$lookup': {
                                            'from': 'chapter',
                                            'let': {
                                                'chapter_id': '$_id'
                                            },
                                            'pipeline': [
                                                {
                                                    '$set': {
                                                        'id': {
                                                            '$toString': '$_id'
                                                        }
                                                    },
                                                },
                                                {
                                                    '$match': {
                                                        '$expr': {
                                                            '$eq': ['$id', '$$chapter_id']
                                                        }
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
                                            'name': '$chapter_info.name'
                                        }
                                    }
                                ],
                                'as': 'chapters'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': '$_id',
                                'name': '$class_info.name',
                                'chapters': 1
                            }
                        }
                    ],
                    'as': 'classes'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'id': '$_id',
                    'name': '$subject_info.name',
                    'classes': 1
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

        classify_data = questions_db[GROUP_QUESTIONS].aggregate(pipeline)

        if classify_data.alive:
            result_data = classify_data.next().get('data')
            return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'classify not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=============COMMUNITY_GET_QUESTION_CLASSIFY============
#========================================================
@app.get(
    path='/community/get_question_classify',
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
async def community_get_question_classify(
    # data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$subject_id'
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'let': {
                        'subject_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            },
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$subject_id']
                                }
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
                '$lookup': {
                    'from': 'community_questions',
                    'let': {
                        'subject_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$subject_id', '$$subject_id']
                                }
                            }
                        },
                        {
                            '$group': {
                                '_id': '$class_id'
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'class',
                                'let': {
                                    'class_id': '$_id'
                                },
                                'pipeline': [
                                    {
                                        '$set': {
                                            'id': {
                                                '$toString': '$_id'
                                            }
                                        },
                                    },
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$id', '$$class_id']
                                            }
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
                            '$lookup': {
                                'from': 'community_questions',
                                'let': {
                                    'class_id': '$_id'
                                },
                                'pipeline': [
                                    {
                                        '$match': {
                                            '$expr': {
                                                '$eq': ['$class_id', '$$class_id']
                                            }
                                        }
                                    },
                                    {
                                        '$group': {
                                            '_id': '$chapter_id',
                                        }
                                    },
                                    {
                                        '$lookup': {
                                            'from': 'chapter',
                                            'let': {
                                                'chapter_id': '$_id'
                                            },
                                            'pipeline': [
                                                {
                                                    '$set': {
                                                        'id': {
                                                            '$toString': '$_id'
                                                        }
                                                    },
                                                },
                                                {
                                                    '$match': {
                                                        '$expr': {
                                                            '$eq': ['$id', '$$chapter_id']
                                                        }
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
                                            'name': '$chapter_info.name'
                                        }
                                    }
                                ],
                                'as': 'chapters'
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': '$_id',
                                'name': '$class_info.name',
                                'chapters': 1
                            }
                        }
                    ],
                    'as': 'classes'
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'id': '$_id',
                    'name': '$subject_info.name',
                    'classes': 1
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

        classify_data = questions_db[COMMUNITY_QUESTIONS].aggregate(pipeline)

        if classify_data.alive:
            result_data = classify_data.next().get('data')
            return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'Không tìm thấy!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
