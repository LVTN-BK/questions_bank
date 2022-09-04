from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from configs.logger import logger
from configs.settings import (CHAPTER, CLASS, QUESTIONS, SUBJECT, TAG_COLLECTION,
                              app, classify_db, questions_db)
from fastapi import Depends, Path, Query, status
from models.define.classify import ClassifyOwnerType

from starlette.responses import JSONResponse



#========================================================
#===================USER_GET_CLASSIFY====================
#========================================================
@app.get(
    path='/get_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify - user']
)
async def get_classify(
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    'user_id': data2.get('user_id'),
                    'owner_type': ClassifyOwnerType.USER
                }
            },
            {
                '$addFields': {
                    'subject_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'localField': 'subject_id',
                    'foreignField': 'subject_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'class_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'localField': 'class_id',
                                'foreignField': 'class_id',
                                'pipeline': [
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': {
                                                '$toString': '$_id'
                                            },
                                            'name': 1
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
                                'id': {
                                    '$getField': 'class_id'
                                },
                                'name': 1,
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
                    'id': {
                        '$getField': 'subject_id'
                    },
                    'name': 1,
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

        all_subject = classify_db[SUBJECT].aggregate(pipeline)
        result = []
        if all_subject.alive:
            result = all_subject.next().get('data')

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===================GROUP_GET_CLASSIFY===================
#========================================================
@app.get(
    path='/group_get_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify - group']
)
async def group_get_classify(
    group_id: str = Query(..., description='ID of group'),
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    'group_id': group_id,
                    'owner_type': ClassifyOwnerType.GROUP
                }
            },
            {
                '$addFields': {
                    'subject_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'localField': 'subject_id',
                    'foreignField': 'subject_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'class_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'localField': 'class_id',
                                'foreignField': 'class_id',
                                'pipeline': [
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': {
                                                '$toString': '$_id'
                                            },
                                            'name': 1
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
                                'id': {
                                    '$getField': 'class_id'
                                },
                                'name': 1,
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
                    'id': {
                        '$getField': 'subject_id'
                    },
                    'name': 1,
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

        all_subject = classify_db[SUBJECT].aggregate(pipeline)
        result = []
        if all_subject.alive:
            result = all_subject.next().get('data')

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=================COMMUNITY_GET_CLASSIFY=================
#========================================================
@app.get(
    path='/community_get_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify - community']
)
async def community_get_classify(
    data2: dict = Depends(valid_headers)
):
    try:
        pipeline = [
            {
                '$match': {
                    'owner_type': ClassifyOwnerType.COMMUNITY
                }
            },
            {
                '$addFields': {
                    'subject_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'localField': 'subject_id',
                    'foreignField': 'subject_id',
                    'pipeline': [
                        {
                            '$addFields': {
                                'class_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$lookup': {
                                'from': 'chapter',
                                'localField': 'class_id',
                                'foreignField': 'class_id',
                                'pipeline': [
                                    {
                                        '$project': {
                                            '_id': 0,
                                            'id': {
                                                '$toString': '$_id'
                                            },
                                            'name': 1
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
                                'id': {
                                    '$getField': 'class_id'
                                },
                                'name': 1,
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
                    'id': {
                        '$getField': 'subject_id'
                    },
                    'name': 1,
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

        all_subject = classify_db[SUBJECT].aggregate(pipeline)
        result = []
        if all_subject.alive:
            result = all_subject.next().get('data')

        return JSONResponse(content={'status': 'success', 'data': result},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
