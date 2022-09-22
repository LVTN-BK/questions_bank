from datetime import datetime
from math import ceil
from typing import List
from app.utils.classify_utils.classify_create import get_user_classify_other_id, user_import_classify
from configs.logger import logger
from models.db.question import Questions_DB, Questions_Evaluation_DB, Questions_Version_DB
from models.define.exam import ManageExamEvaluationStatus
from models.define.question import ImportQuestionClassifyMode, ManageQuestionLevel, ManageQuestionType
from configs.settings import ANSWERS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, questions_db, classify_db, TAG_COLLECTION
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from models.request.question import DATA_Auto_Pick_Question, DATA_Evaluate_Question, DATA_Import_Question, DATA_Reject_Update_Question_Level, DATA_Update_Question_Level


def auto_pick_question(data: List[DATA_Auto_Pick_Question]):
    try:
        result = []
        result_id = []
        for selec in data:
            flag = True
            while flag:
                pipeline_head = [
                    {
                        '$set': {
                            '_id': {
                                '$toString': '$_id'
                            }
                        }
                    },
                    {
                        '$match': {
                            'chapter_id': selec.chapter_id,
                            'type': {
                                '$in': selec.type
                            },
                            '_id': {
                                '$not': {
                                    '$in': result_id
                                }
                            }
                        }
                    }
                ]
                facet_body = {}
                for key in selec.level.keys():
                    if selec.level.get(key):
                        facet_body[key] = [
                            {
                                '$match': {
                                    'level': key
                                }
                            },
                            {
                                '$sample': {
                                    'size': selec.level.get(key)
                                }
                            },
                            {
                                '$group': {
                                    '_id': {
                                        '$toString': '$_id'
                                    },
                                    'user_id': {
                                        '$first': '$user_id'
                                    },
                                    'subject_id': {
                                        '$first': '$subject_id'
                                    },
                                    'class_id': {
                                        '$first': '$class_id'
                                    },
                                    'chapter_id': {
                                        '$first': '$chapter_id'
                                    },
                                    'type': {
                                        '$first': '$type'
                                    },
                                    'tag_id': {
                                        '$first': '$tag_id'
                                    },
                                    'level': {
                                        '$first': '$level'
                                    },
                                    'datetime_created': {
                                        '$first': '$datetime_created'
                                    },
                                }
                            }
                        ]

                pipeline_facet = [
                    {
                        '$facet': facet_body
                    }
                ]

                pipeline = pipeline_head + pipeline_facet
                res_data = questions_db[QUESTIONS].aggregate(pipeline)
                flag = False
                if res_data.alive:
                    res_data = res_data.next()
                    logger().info(f'res_data; {res_data}')

                    more_data = []
                    for key in selec.level.keys():
                        if res_data.get(key):
                            more_data += res_data.get(key)
                            selec.level[key] = selec.level.get(key) - len(res_data.get(key))
                        if selec.level[key]:
                            flag = True
                    logger().info(more_data)
                    logger().info(selec.level)
                    if more_data:
                        result += more_data
                        for x in more_data:
                            result_id.append(x.get('_id'))
                    else:
                        raise Exception(f'Không có đủ câu hỏi!')
                    logger().info(result_id)
                else:
                    raise Exception('Có lỗi xảy ra!')
                
        pipeline = [
            {
                '$set': {
                    'question_id': {
                        '$toString': '$_id'
                    }
                }
            },
            {
                '$match': {
                    'question_id': {
                        '$in': result_id
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'tag',
                    'let': {
                        'list_tag_id': '$tag_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$in': ['$id', '$$list_tag_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'tags_info'
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'let': {
                        'subject_id': '$subject_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$subject_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'subject_info'
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'let': {
                        'class_id': '$class_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$class_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'class_info'
                }
            },
            {
                '$lookup': {
                    'from': 'chapter',
                    'let': {
                        'chapter_id': '$chapter_id'
                    },
                    'pipeline': [
                        {
                            '$set': {
                                'id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$id', '$$chapter_id']
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': 1,
                                'name': 1
                            }
                        }
                    ],
                    'as': 'chapter_info'
                }
            },
            {
                '$lookup': {
                    'from': 'questions_version',
                    'localField': 'question_id',
                    'foreignField': 'question_id',
                    'pipeline': [
                        {
                            '$match' : {
                                'is_latest': True
                            }
                        }
                    ],
                    'as': 'ques_ver'
                }
            },
            {
                '$unwind': '$ques_ver'
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'subject_info': {
                        '$first': '$subject_info'
                    },
                    'class_info': {
                        '$first': '$class_info'
                    },
                    'chapter_info': {
                        '$first': '$chapter_info'
                    },
                    'level': 1,
                    'question_id': 1,
                    'question_version_id': {
                        '$toString': '$ques_ver._id'
                    },
                    'version_name': '$ques_ver.version_name',
                    "question_content": '$ques_ver.question_content',
                    # "question_image": '$ques_ver.question_image',
                    'question_type': "$type",
                    'tags_info': "$tags_info",
                    'answers': '$ques_ver.answers',
                    'answers_right': '$ques_ver.answers_right',
                    'sample_answer': '$ques_ver.sample_answer',
                    'display': '$ques_ver.display',
                    'datetime_created': "$datetime_created"
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
        question_data = questions_db[QUESTIONS].aggregate(pipeline)
        if question_data.alive:
            all_data = question_data.next()
            result_data = all_data.get('data')
            return result_data
        else:
            raise Exception('Có lỗi xảy ra!')
    except Exception as e:
        logger().error(e)
        raise Exception('Có lỗi xảy ra!')
