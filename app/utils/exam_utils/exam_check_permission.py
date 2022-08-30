from configs.logger import logger
from models.define.question import ManageQuestionType
from configs.settings import EXAMS, exams_db
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