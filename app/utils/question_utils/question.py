from configs.logger import logger
from models.define.question import ManageQuestionType
from configs.settings import ANSWERS, QUESTIONS, QUESTIONS_VERSION, questions_db
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

def get_question_information_with_version_id(question_version_id: str):
    # find question version
    question_version = questions_db[QUESTIONS_VERSION].find_one(
        {
            '_id': ObjectId(question_version_id)
        },
    )
    if not question_version:
        return {}

    # find question
    question = questions_db[QUESTIONS].find_one(
        {
            '_id': ObjectId(question_version.get('question_id'))
        }
    )
    if not question:
        return {}
    
    # get answer of question
    answers = get_answer(answers=question_version.get('answers'), question_type=question.get('type'))

    logger().info(answers)
    question_version['answers'] = answers
    question_version['type'] = question.get('type')
    del question_version['_id']
    
    return question_version