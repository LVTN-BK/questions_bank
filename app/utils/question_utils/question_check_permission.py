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