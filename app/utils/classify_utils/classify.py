from app.utils.group_utils.group import check_owner_or_user_of_group
from configs.logger import logger
from configs.settings import CHAPTER, CLASS, SUBJECT, classify_db
from bson import ObjectId

from models.define.classify import ClassifyOwnerType


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

def check_permission_with_subject(user_id: str, subject_id: str):
    try:
        res = classify_db[SUBJECT].find_one({'_id': ObjectId(subject_id)})
        if not res:
            return False
        if (res.get('owner_type') == ClassifyOwnerType.USER) or (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
            if user_id != res.get('user_id'):
                return False
            else:
                return True
        else:
            if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                return False
            else:
                return True
    except Exception as e:
        logger().error(e)
        return False

def check_permission_with_class(user_id: str, class_id: str):
    try:
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(class_id)
                }
            },
            {
                '$set': {
                    'subject_object_id': {
                        '$toObjectId': '$subject_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'localField': 'subject_object_id',
                    'foreignField': '_id',
                    'as': 'subject_info'
                }
            },
            {
                '$unwind': 'subject_info'
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'group_id': '$subject_info.group_id',
                    'owner_type': '$subject_info.owner_type',
                }
            }
        ]
        res = classify_db[CLASS].aggregate(pipeline)
        if res.alive:
            res = res.next()
            if (res.get('owner_type') == ClassifyOwnerType.USER) or (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
                # check owner of class
                if user_id != res.get('user_id'):
                    return False
                else:
                    return True
            else:
                if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                    return False
                else:
                    return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False

def check_permission_with_chapter(user_id: str, chapter_id: str):
    try:
        pipeline = [
            {
                '$match': {
                    '_id': ObjectId(chapter_id)
                }
            },
            {
                '$set': {
                    'class_object_id': {
                        '$toObjectId': '$subject_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'class',
                    'localField': 'class_object_id',
                    'foreignField': '_id',
                    'as': 'class_info'
                }
            },
            {
                '$unwind': '$class_info'
            },
            {
                '$set': {
                    'subject_object_id': {
                        '$toObjectId': '$class_info.subject_id'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'subject',
                    'localField': 'subject_object_id',
                    'foreignField': '_id',
                    'as': 'subject_info'
                }
            },
            {
                '$unwind': 'subject_info'
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'group_id': '$subject_info.group_id',
                    'owner_type': '$subject_info.owner_type',
                }
            }
        ]
        res = classify_db[CHAPTER].aggregate(pipeline)
        if res.alive:
            res = res.next()
            if (res.get('owner_type') == ClassifyOwnerType.USER) or (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
                # check owner of chapter
                if user_id != res.get('user_id'):
                    return False
                else:
                    return True
            else:
                if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                    return False
                else:
                    return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False
