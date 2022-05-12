from configs.logger import logger
from models.define.question import ManageQuestionType
from configs.settings import ANSWERS, questions_db
from bson import ObjectId


def get_answer(answers, question_type):
    try:
        if question_type in [ManageQuestionType.MULTICHOICE, ManageQuestionType.SORT]:
            result = []
            for answer_id in answers:
                answer_info = questions_db[ANSWERS].find_one(
                    {
                        '_id': ObjectId(answer_id)
                    }
                )

                if answer_info:
                    answer_info['_id'] = str(answer_info['_id'])
                    result.append(answer_info)
                else:
                    answer_info.append({})
            return result
        elif question_type == ManageQuestionType.MATCHING:
            left = []
            right = []
            for answer_id in answers.get('left'):
                answer_info = questions_db[ANSWERS].find_one(
                    {
                        '_id': ObjectId(answer_id)
                    }
                )
                if answer_info:
                    answer_info['_id'] = str(answer_info['_id'])
                    left.append(answer_info)
                else:
                    left.append({})
            for answer_id in answers.get('right'):
                answer_info = questions_db[ANSWERS].find_one(
                    {
                        '_id': ObjectId(answer_id)
                    }
                )
                if answer_info:
                    answer_info['_id'] = str(answer_info['_id'])
                    right.append(answer_info)
                else:
                    right.append({})
            result = {
                'left': left,
                'right': right
            }
            return result
        return None
    except Exception as e:
        logger().error(e)
        return None
