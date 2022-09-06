from app.utils._header import valid_headers
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_exam, get_list_group_question
from configs.logger import logger
from configs.settings import (EXAMS, GROUP_EXAMS,
                              app, questions_db)
from fastapi import Depends, Query, status
from starlette.responses import JSONResponse



#========================================================
#==================USER_GET_EXAM_CLASSIFY================
#========================================================
@app.get(
    path='/user/get_exam_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - classify']
)
async def user_get_exam_classify(
    data2: dict = Depends(valid_headers)
):
    try:
        filter_exam = [{}]

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

        
        
        pipeline = [
            {
                '$match': {
                    '$and': filter_exam
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
                    'from': 'exams',
                    'let': {
                        'subject_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$and': filter_exam
                            }
                        },
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
                            '$project': {
                                '_id': 0,
                                'id': '$_id',
                                'name': '$class_info.name'
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

        classify_data = questions_db[EXAMS].aggregate(pipeline)

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
#=================GROUP_GET_EXAM_CLASSIFY================
#========================================================
@app.get(
    path='/group/get_exam_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - classify']
)
async def group_get_exam_classify(
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
                    'from': 'group_exams',
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
                            '$project': {
                                '_id': 0,
                                'id': '$_id',
                                'name': '$class_info.name'
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

        classify_data = questions_db[GROUP_EXAMS].aggregate(pipeline)

        if classify_data.alive:
            result_data = classify_data.next().get('data')
            return JSONResponse(content={'status': 'success', 'data': result_data},status_code=status.HTTP_200_OK)
        else:
            msg = 'classify not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
