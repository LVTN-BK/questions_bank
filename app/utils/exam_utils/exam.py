from datetime import datetime
from typing import List
from configs.logger import logger
from configs.settings import COMMUNITY_EXAMS, EXAMS, EXAMS_EVALUATION, GROUP_EXAMS, QUESTIONS_EVALUATION, exams_db
from models.db.question import Questions_Evaluation_DB
from models.define.question import ManageQuestionLevel
from fastapi.encoders import jsonable_encoder
from bson import ObjectId


def remove_exam(user_id: str, list_exam_ids: List[str]):
    all_id = []
    # find question
    for exam_id in list_exam_ids:
        exam_del = exams_db[EXAMS].find_one_and_update(
            {
                "_id": ObjectId(exam_id),
                'user_id': user_id   
            },
            {
                '$set': {
                    'is_removed': True
                }
            }
        )

        if exam_del:
            all_id.append(exam_id)
    
            # # find exam version
            # exam_version = exams_db[EXAMS_VERSION].delete_many(
            #     {
            #         'exam_id': exam_id
            #     }
            # )
    # delete exam in group
    exams_db[GROUP_EXAMS].delete_many(
        {
            'exam_id': {
                '$in': all_id
            }
        }
    )

    # delete exam in community
    exams_db[COMMUNITY_EXAMS].delete_many(
        {
            'exam_id': {
                '$in': all_id
            }
        }
    )