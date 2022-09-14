from datetime import datetime
from configs.logger import logger
from configs.settings import EXAMS_EVALUATION, QUESTIONS_EVALUATION, exams_db
from models.db.question import Questions_Evaluation_DB
from models.define.question import ManageQuestionLevel
from fastapi.encoders import jsonable_encoder


def get_probability_irt(sum: int, size: int, n: int):
    p = sum/size
    if p == 1:
        p = 1-1/n
    elif p == 0:
        p = 1/n
    return p

def evaluate_irt(p):
    import math
    eval = math.log(p/(1-p))
    return eval

def get_item_level_name(b):
            
    if b <= -2:
        return ManageQuestionLevel.VERY_EASY
    elif b < -0.5:
        return ManageQuestionLevel.EASY
    elif b <= 0.5:
        return ManageQuestionLevel.MEDIUM
    elif b < 2:
        return ManageQuestionLevel.HARD
    else:
        return ManageQuestionLevel.VERY_HARD


#==================EVALUATE_QUESTION================
def insert_question_evaluate(user_id, question_ids, difficult_params, probabilities, ability, num_student):
    try:
        # save difficult_value
        for x in range(len(question_ids)):
            evaluate_question_data = Questions_Evaluation_DB(
                question_id=question_ids[x],
                user_id=user_id,
                correct_probability=round(probabilities[x], 3),
                num_student=num_student,
                average_ability=round(ability, 3),
                difficult_value=round(difficult_params[x], 3),
                recommend_level=get_item_level_name(b = difficult_params[x]),
                datetime_created=datetime.now().timestamp()
            )

            # update current latest question evaluation
            update_question_evaluation = exams_db[QUESTIONS_EVALUATION].find_one_and_update(
                {
                    'question_id': question_ids[x],
                    'user_id': user_id,
                    'is_latest': True
                },
                {
                    '$set': {
                        'is_latest': False
                    }
                }
            )

            # insert evaluation into db
            exams_db[QUESTIONS_EVALUATION].insert_one(jsonable_encoder(evaluate_question_data))
    except Exception as e:
        logger().error(e)


def insert_exam_evaluate(exam_id: str, user_id: str, data: dict):
    try:
        # update current latest question evaluation
        # update_question_evaluation = exams_db[EXAMS_EVALUATION].find_one_and_update(
        #     {
        #         'exam_id': exam_id,
        #         'user_id': user_id,
        #         'is_latest': True
        #     },
        #     {
        #         '$set': {
        #             'is_latest': False
        #         }
        #     }
        # )

        data_insert_exam = {
            'user_id': user_id,
            'exam_id': data.get('exam_id'),
            'datetime_created': data.get('datetime')
        }
        # insert evaluation into db
        insert_exam_id = exams_db[EXAMS_EVALUATION].insert_one(data_insert_exam).inserted_id
        
        # insert to question evaluation
        for data_question in data.get('data'):
            data_question.update(
                {
                    'user_id': user_id,
                    'evaluation_id': str(insert_exam_id),
                    'datetime_created': data.get('datetime')
                }
            )
            exams_db[QUESTIONS_EVALUATION].insert_one(data_question)



        # data.update(
        #     {
        #         'user_id': user_id,
        #         'is_latest': True,
        #     }
        # )

        
    except Exception as e:
        logger().error(e)