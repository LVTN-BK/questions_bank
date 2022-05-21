from configs.logger import logger
from configs.settings import CHAPTER, CLASS, SUBJECT, classify_db
from bson import ObjectId


def get_chapter_info(chapter_id: str):
    try:
        res = classify_db[CHAPTER].find_one({'_id': ObjectId(chapter_id)})
        res['_id'] = str(res['_id'])
        return res
    except Exception as e:
        logger().error(e)
        return {}

def get_class_info(class_id: str):
    try:
        res = classify_db[CLASS].find_one({'_id': ObjectId(class_id)})
        res['_id'] = str(res['_id'])
        return res
    except Exception as e:
        logger().error(e)
        return {}

def get_subject_info(subject_id: str):
    try:
        res = classify_db[SUBJECT].find_one({'_id': ObjectId(subject_id)})
        res['_id'] = str(res['_id'])
        return res
    except Exception as e:
        logger().error(e)
        return {}