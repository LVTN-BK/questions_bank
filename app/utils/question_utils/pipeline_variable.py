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