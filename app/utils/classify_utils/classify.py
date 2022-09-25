from datetime import datetime
from app.utils.account_utils.user import check_is_admin
from app.utils.group_utils.group import check_owner_or_user_of_group
from configs.logger import logger
from configs.settings import CHAPTER, CLASS, SUBJECT, classify_db
from bson import ObjectId
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from fastapi.encoders import jsonable_encoder

from models.define.classify import ClassifyDefaultValue, ClassifyOwnerType


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
            return False, None
        if (res.get('owner_type') == ClassifyOwnerType.USER):
            if user_id != res.get('user_id'):
                return False, res.get('owner_type')
            else:
                return True, res.get('owner_type')
        elif (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
            if check_is_admin(user_id=user_id):
                return True, res.get('owner_type')
            else:
                return False, res.get('owner_type')
        else:
            if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                return False, res.get('owner_type')
            else:
                return True, res.get('owner_type')
    except Exception as e:
        logger().error(e)
        return False, None

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
                '$unwind': '$subject_info'
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
            if (res.get('owner_type') == ClassifyOwnerType.USER):
                if user_id != res.get('user_id'):
                    return False, res.get('owner_type')
                else:
                    return True, res.get('owner_type')
            elif (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
                if check_is_admin(user_id=user_id):
                    return True, res.get('owner_type')
                else:
                    return False, res.get('owner_type')
            else:
                if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                    return False, res.get('owner_type')
                else:
                    return True, res.get('owner_type')
        else:
            return False, None
    except Exception as e:
        logger().error(e)
        return False, None

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
                        '$toObjectId': '$class_id'
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
                '$unwind': '$subject_info'
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
            logger().info(res)
            if (res.get('owner_type') == ClassifyOwnerType.USER):
                if user_id != res.get('user_id'):
                    return False, res.get('owner_type')
                else:
                    return True, res.get('owner_type')
            elif (res.get('owner_type') == ClassifyOwnerType.COMMUNITY):
                if check_is_admin(user_id=user_id):
                    return True, res.get('owner_type')
                else:
                    return False, res.get('owner_type')
            else:
                if not check_owner_or_user_of_group(user_id=user_id, group_id=res.get('group_id')):
                    return False, res.get('owner_type')
                else:
                    return True, res.get('owner_type')
        else:
            return False, None
    except Exception as e:
        logger().error(e)
        return False, None

def get_group_classify_other_id(group_id: str, user_id: str):
    # subject other
    subject_info = classify_db[SUBJECT].find_one({
        'group_id': group_id,
        'owner_type': ClassifyOwnerType.GROUP,
        'name': ClassifyDefaultValue.OTHER
    })

    if subject_info:
        subject_id = str(subject_info.get('_id'))
    else:
        subject_data = Subjects_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            group_id=group_id,
            owner_type=ClassifyOwnerType.GROUP,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        subject_id = str(inserted_subject_id)

    # class other
    class_info = classify_db[CLASS].find_one({
        'subject_id': subject_id,
        'name': ClassifyDefaultValue.OTHER
    })

    if class_info:
        class_id = str(class_info.get('_id'))
    else:
        class_data = Class_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            subject_id=subject_id,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_class_id = classify_db[CLASS].insert_one(jsonable_encoder(class_data)).inserted_id
        class_id = str(inserted_class_id)

    # chapter other
    chapter_info = classify_db[CHAPTER].find_one({
        'class_id': class_id,
        'name': ClassifyDefaultValue.OTHER
    })

    if chapter_info:
        chapter_id = str(chapter_info.get('_id'))
    else:
        chapter_data = Chapters_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            class_id=class_id,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_chapter_id = classify_db[CHAPTER].insert_one(jsonable_encoder(chapter_data)).inserted_id
        chapter_id = str(inserted_chapter_id)
    return subject_id, class_id, chapter_id

def get_community_classify_other_id(user_id: str):
    # subject other
    subject_info = classify_db[SUBJECT].find_one({
        'owner_type': ClassifyOwnerType.COMMUNITY,
        'name': ClassifyDefaultValue.OTHER
    })

    if subject_info:
        subject_id = str(subject_info.get('_id'))
    else:
        subject_data = Subjects_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            owner_type=ClassifyOwnerType.COMMUNITY,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        subject_id = str(inserted_subject_id)

    # class other
    class_info = classify_db[CLASS].find_one({
        'subject_id': subject_id,
        'name': ClassifyDefaultValue.OTHER
    })

    if class_info:
        class_id = str(class_info.get('_id'))
    else:
        class_data = Class_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            subject_id=subject_id,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_class_id = classify_db[CLASS].insert_one(jsonable_encoder(class_data)).inserted_id
        class_id = str(inserted_class_id)

    # chapter other
    chapter_info = classify_db[CHAPTER].find_one({
        'class_id': class_id,
        'name': ClassifyDefaultValue.OTHER
    })

    if chapter_info:
        chapter_id = str(chapter_info.get('_id'))
    else:
        chapter_data = Chapters_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            class_id=class_id,
            datetime_created=datetime.now().timestamp(),
        )
        inserted_chapter_id = classify_db[CHAPTER].insert_one(jsonable_encoder(chapter_data)).inserted_id
        chapter_id = str(inserted_chapter_id)
    return subject_id, class_id, chapter_id

def check_classify_is_valid(subject_id: str, class_id: str, chapter_id: str):
    try:
        subject_id = ObjectId(subject_id)
        class_id = ObjectId(class_id)
        chapter_id = ObjectId(chapter_id)
        return True
    except Exception as e:
        logger().error(e)
        return False

