LOOKUP_CLASS_FROM_QUESTIONS = {
    '$lookup': { #join with class collection
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
}

LOOKUP_SUBJECT_FROM_QUESTIONS = {
    '$lookup': { #join with subject collection
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
LOOKUP_CHAPTER_FROM_QUESTIONS = {
    '$lookup': { #join with chapter collection
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

def get_pipeline_list_question_facet(limit: int, num_skip: int):
    list_question_facet = [
        { 
            '$facet' : {
                'metadata': [ 
                    { 
                        '$count': "total" 
                    }, 
                    { 
                        '$addFields': { 
                            'page': {
                                '$toInt': {
                                    '$ceil': {
                                        '$divide': ['$total', limit]
                                    }
                                }
                            }
                        } 
                    } 
                ],
                'data': [ 
                    {
                        '$project': {
                            '_id': 0,
                            'question_id': 1,
                            'question_version_id': {
                                '$toString': '$_id'
                            },
                            'version_name': 1,
                            "question_content": 1,
                            'level': "$question_information.level",
                            'question_type': "$question_information.type",
                            'tags_info': "$question_information.tags_info",
                            'is_public': "$question_information.is_public",
                            'answers': 1,
                            'answers_right': 1,
                            'sample_answer': 1,
                            'display': 1,
                            'datetime_shared': "$question_information.datetime_shared",
                            'datetime_created': "$question_information.datetime_created"
                        }
                    },
                    {
                        '$sort': {
                            'datetime_created': -1
                        }
                    },
                    { 
                        '$skip': num_skip 
                    },
                    { 
                        '$limit': limit 
                    } 
                ] # add projection here wish you re-shape the docs
            } 
        },
        {
            '$unwind': '$metadata'
        },
    ]
    return list_question_facet