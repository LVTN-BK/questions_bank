from datetime import datetime
from app.utils.group_utils.group import check_owner_or_user_of_group
from configs.logger import logger
from configs.settings import CHAPTER, CLASS, SUBJECT, classify_db
from bson import ObjectId
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from fastapi.encoders import jsonable_encoder

from models.define.classify import ClassifyDefaultValue, ClassifyOwnerType



def get_user_classify_other_id(user_id: str):
    # subject other
    subject_info = classify_db[SUBJECT].find_one({
        'owner_type': ClassifyOwnerType.USER,
        'name': ClassifyDefaultValue.OTHER,
        'user_id': user_id
    })

    if subject_info:
        subject_id = str(subject_info.get('_id'))
    else:
        subject_data = Subjects_DB(
            name=ClassifyDefaultValue.OTHER,
            user_id=user_id,
            owner_type=ClassifyOwnerType.USER,
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


def user_import_classify(subject_id: str, class_id: str, chapter_id: str, user_id: str):
    try:
        subject_data = classify_db[SUBJECT].find_one({'_id': ObjectId(subject_id)})
        class_data = classify_db[CLASS].find_one({'_id': ObjectId(class_id)})
        chapter_data = classify_db[CHAPTER].find_one({'_id': ObjectId(chapter_id)})
        if subject_data and class_data and chapter_data:
            subject_name = subject_data.get('name')
            user_subject = classify_db[SUBJECT].find_one(
                {
                    'user_id': user_id,
                    'name': subject_name,
                    'owner_type': ClassifyOwnerType.USER
                }
            )
            if user_subject:
                id_subject = str(user_subject.get('_id'))
            else:
                subject_data = Subjects_DB(
                    name=subject_name,
                    user_id=user_id,
                    owner_type=ClassifyOwnerType.USER,
                    datetime_created=datetime.now().timestamp(),
                )
                id_insert_subject = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
                id_subject = str(id_insert_subject)

            # class
            class_name = class_data.get('name')
            user_class = classify_db[CLASS].find_one(
                {
                    'user_id': user_id,
                    'subject_id': id_subject,
                    'name': class_name,
                }
            )
            if user_class:
                id_class = str(user_class.get('_id'))
            else:
                class_data = Class_DB(
                    name=class_name,
                    user_id=user_id,
                    subject_id=id_subject,
                    datetime_created=datetime.now().timestamp(),
                )
                id_insert_class = classify_db[CLASS].insert_one(jsonable_encoder(class_data)).inserted_id
                id_class = str(id_insert_class)
            
            # chapter
            chapter_name = chapter_data.get('name')
            user_chapter = classify_db[CHAPTER].find_one(
                {
                    'user_id': user_id,
                    'class_id': id_class,
                    'name': chapter_name,
                }
            )
            if user_chapter:
                id_chapter = str(user_chapter.get('_id'))
            else:
                chapter_data = Chapters_DB(
                    name=chapter_name,
                    user_id=user_id,
                    subject_id=id_subject,
                    datetime_created=datetime.now().timestamp(),
                )
                id_insert_chapter = classify_db[CHAPTER].insert_one(jsonable_encoder(chapter_data)).inserted_id
                id_chapter = str(id_insert_chapter)
            return id_subject, id_class, id_chapter
        else:
            return get_user_classify_other_id(user_id=user_id)
    except Exception:
        return get_user_classify_other_id(user_id=user_id)


