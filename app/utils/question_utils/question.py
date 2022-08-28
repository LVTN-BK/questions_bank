from math import ceil
from configs.logger import logger
from models.define.question import ManageQuestionLevel, ManageQuestionType
from configs.settings import ANSWERS, QUESTIONS, QUESTIONS_VERSION, questions_db, classify_db, TAG_COLLECTION
from bson import ObjectId


def get_list_tag_id_from_input(list_tag: list):
    try:
        result = []
        for tag_object in list_tag:
            if tag_object.get('isNew'):
                # upsert tag
                tag_data = classify_db[TAG_COLLECTION].find_one(
                    {
                        'name': tag_object.get('name')
                    }
                )
                if tag_data:
                    result.append(str(tag_data.get('_id')))
                else:
                    insert_id = classify_db[TAG_COLLECTION].insert_one(
                        {
                            'name': tag_object.get('name')
                        }
                    ).inserted_id
                    result.append(str(insert_id))
            else:
                result.append(tag_object.get('id'))
            
        return result
    except Exception as e:
        logger().error(e)
        return []

def get_answer(answers, question_type):
    try:
        if question_type in [ManageQuestionType.MULTICHOICE, ManageQuestionType.SORT]:
            pipeline = [
                {
                    '$addFields': {
                        'answer_id': {
                            '$toString': '$_id'
                        }
                    }
                },
                {
                    '$match': {
                        '$expr': {
                            '$in': ['$answer_id', answers]
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'answer_id': 1,
                        'answer_image': 1,
                        'answer_content': 1,
                        'datetime_created': 1
                    }
                }
            ]
            list_answers = questions_db[ANSWERS].aggregate(pipeline)
            result = []
            for answer_info in list_answers:
                result.append(answer_info)
            return result
            # for answer_id in answers:
            #     answer_info = questions_db[ANSWERS].find_one(
            #         {
            #             '_id': ObjectId(answer_id)
            #         }
            #     )

            #     if answer_info:
            #         answer_info['_id'] = str(answer_info['_id'])
            #         result.append(answer_info)
            #     else:
            #         answer_info.append({})
            # return result
        elif question_type == ManageQuestionType.MATCHING:
            left = []
            right = []
            pipeline_left = [
                {
                    '$addFields': {
                        'answer_id': {
                            '$toString': '$_id'
                        }
                    }
                },
                {
                    '$match': {
                        '$expr': {
                            '$in': ['$answer_id', answers.get('left')]
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'answer_id': 1,
                        'answer_image': 1,
                        'answer_content': 1,
                        'datetime_created': 1
                    }
                }
            ]
            list_answers_left = questions_db[ANSWERS].aggregate(pipeline_left)
            for answer_info in list_answers_left:
                left.append(answer_info)
            
            
            pipeline_right = [
                {
                    '$addFields': {
                        'answer_id': {
                            '$toString': '$_id'
                        }
                    }
                },
                {
                    '$match': {
                        '$expr': {
                            '$in': ['$answer_id', answers.get('right')]
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'answer_id': 1,
                        'answer_image': 1,
                        'answer_content': 1,
                        'datetime_created': 1
                    }
                }
            ]
            list_answers_right = questions_db[ANSWERS].aggregate(pipeline_right)
            for answer_info in list_answers_right:
                right.append(answer_info)





            # for answer_id in answers.get('left'):
            #     answer_info = questions_db[ANSWERS].find_one(
            #         {
            #             '_id': ObjectId(answer_id)
            #         }
            #     )
            #     if answer_info:
            #         answer_info['_id'] = str(answer_info['_id'])
            #         left.append(answer_info)
            #     else:
            #         left.append({})
            # for answer_id in answers.get('right'):
            #     answer_info = questions_db[ANSWERS].find_one(
            #         {
            #             '_id': ObjectId(answer_id)
            #         }
            #     )
            #     if answer_info:
            #         answer_info['_id'] = str(answer_info['_id'])
            #         right.append(answer_info)
            #     else:
            #         right.append({})
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

def get_query_filter_questions(search, type, level, class_id, subject_id, chapter_id, tags):
    filter_question = [{}]
    filter_question_version = [{}]

    # =============== tags =================
    if tags:
        query_search = {
            'tag_id': {
                '$in': tags,
            }
        }
        filter_question.append(query_search)
    
    # =============== search =================
    if search:
        query_search = {
            'question_content': {
                '$regex': search,
                '$options': 'i'
            }
        }
        filter_question_version.append(query_search)
    
    # =============== version =================
    query_latest_version = {
        'is_latest': True
    }
    filter_question_version.append(query_latest_version)

    # =============== status =================
    query_question_status = {
        'is_removed': False
    }
    filter_question.append(query_question_status)

    # =============== type =================
    if type:
        query_question_type = {
            'type': type
        }
        filter_question.append(query_question_type)

    # =============== level =================
    if level:
        query_question_level = {
            'level': level
        }
        filter_question.append(query_question_level)

    # =============== class =================
    if class_id:
        query_question_class = {
            'class_id': class_id
        }
        filter_question.append(query_question_class)

    # =============== subject =================
    if subject_id:
        query_question_subject = {
            'subject_id': subject_id
        }
        filter_question.append(query_question_subject)

    # =============== chapter =================
    if chapter_id:
        if (isinstance(chapter_id, list)):
            query_question_chapter = {
                'chapter_id': {
                    '$in': chapter_id
                }
            }
        else:
            query_question_chapter = {
                'chapter_id': chapter_id
            }
        filter_question.append(query_question_chapter)

    return filter_question, filter_question_version

def get_data_and_metadata(aggregate_response, page):
    result_data = []
    if aggregate_response.alive:
        questions_data = aggregate_response.next()

        result_data = questions_data['data']
        questions_count = questions_data['metadata']['total']
        num_pages = questions_data.get('metadata').get('page')
    else:
        questions_count = 0
        num_pages = 0
    
    meta_data = {
        'count': questions_count,
        'current_page': page,
        'has_next': (num_pages>page),
        'has_previous': (page>1),
        'next_page_number': (page+1) if (num_pages>page) else None,
        'num_pages': num_pages,
        'previous_page_number': (page-1) if (page>1) else None,
        'valid_page': (page>=1) and (page<=num_pages)
    }

    return result_data, meta_data

#==================EVALUATE_QUESTION================
def get_question_evaluation_value(
    num_correct: int,
    num_incorrect: int,
    discrimination: float,      # độ phân biệt câu hỏi (khác 0)
    ability: float,             # năng lực học sinh
    guessing: float             # tham số đoán mò
):
    try:
        import math
        p = num_correct/num_incorrect
        if p>guessing:
            b = ability + math.log((1-guessing)/(p-guessing) - 1)/discrimination
        else:
            b = ability + math.log(1/p - 1)/discrimination
        
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

    except Exception as e:
        logger().error(e)
        return None
