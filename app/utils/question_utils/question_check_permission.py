from configs.logger import logger
from models.define.question import ManageQuestionType
from configs.settings import ANSWERS, QUESTIONS, QUESTIONS_VERSION, questions_db, classify_db, TAG_COLLECTION
from bson import ObjectId


def check_owner_of_question(user_id: str, question_id: str):
    check = questions_db[QUESTIONS].find_one(
        {
            '_id': ObjectId(question_id),
            'user_id': user_id
        }
    )
    if check:
        return True
    else:
        return False
        

def check_owner_of_question_version(user_id: str, question_version_id: str):
    try:
        pipeline=[
            {
                '$match': {
                    '_id': ObjectId(question_version_id),
                }
            },
            {
                '$set': {
                    'question_object_id': {
                        '$toObjectId': '$question_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'questions',
                    'localField': 'question_object_id',
                    'foreignField': '_id',
                    'pipeline': [
                        {
                            '$match': {
                                'user_id': user_id
                            }
                        }
                    ],
                    'as': 'question_info'
                }
            },
            {
                '$unwind': '$question_info'
            }
        ]
        check = questions_db[QUESTIONS_VERSION].aggregate(pipeline)
        if check.alive:
            return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False
