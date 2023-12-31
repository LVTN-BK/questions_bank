from configs.logger import logger
from models.define.question import ManageQuestionType
from configs.settings import COMMUNITY_EXAMS, EXAMS, EXAMS_VERSION, GROUP_PARTICIPANT, exams_db, group_db
from bson import ObjectId


def check_owner_of_exam(user_id: str, exam_id: str):
    check = exams_db[EXAMS].find_one(
        {
            '_id': ObjectId(exam_id),
            'user_id': user_id
        }
    )
    if check:
        return True
    else:
        return False

def check_owner_of_exam_version(user_id: str, exam_version_id: str):
    try:
        pipeline=[
            {
                '$match': {
                    '_id': ObjectId(exam_version_id),
                }
            },
            {
                '$set': {
                    'exam_object_id': {
                        '$toObjectId': '$exam_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'exams',
                    'localField': 'exam_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$match': {
                                'user_id': user_id
                            }
                        }
                    ],
                    'as': 'exam_info'
                }
            },
            {
                '$unwind': '$exam_info'
            }
        ]
        check = exams_db[EXAMS_VERSION].aggregate(pipeline)
        if check.alive:
            return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False

def check_permission_view_exam(exam_id: str, user_id: str):
    exam_data = exams_db[EXAMS].find_one(
        {
            '_id': ObjectId(exam_id),
        }
    )
    if not exam_data:
        raise Exception('exam not found!')
    
    if exam_data.get('user_id') == user_id:
        return True

    # check in community
    community_exam_data = exams_db[COMMUNITY_EXAMS].find_one(
        {
            'exam_id': exam_id,
        }
    )
    if community_exam_data:
        return True

    # check in group
    pipeline = [
        {
            '$match': {
                'user_id': user_id
            }
        },
        {
            '$set': {
                'group_object_id': {
                    '$toObjectId': '$group_id'
                }
            }
        },
        {
            '$lookup': {
                'from': 'group',
                'localField': 'group_object_id',
                'foreignField': '_id',
                'pipeline': [
                    {
                        '$match': {
                            'is_deleted': False
                        }
                    }
                ],
                'as': 'group_data'
            }
        },
        {
            '$unwind': '$group_data'
        },
        {
            '$lookup': {
                'from': 'group_exams',
                'localField': 'group_id',
                'foreignField': 'group_id',
                'pipeline': [
                    {
                        '$match': {
                            'exam_id': exam_id
                        }
                    }
                ],
                'as': 'group_exams_data'
            }
        },
        {
            '$unwind': '$group_exams_data'
        }
    ]
    group_exam = group_db[GROUP_PARTICIPANT].aggregate(pipeline)
    if group_exam.alive:
        return True
    else:
        return False

