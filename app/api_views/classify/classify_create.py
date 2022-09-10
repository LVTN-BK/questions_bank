import copy
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from bson import ObjectId
from app.utils.account_utils.user import check_is_admin
from app.utils.classify_utils.classify import check_permission_with_class, check_permission_with_subject
from app.utils.group_utils.group import check_owner_or_user_of_group
from configs.logger import logger
from configs.settings import (CHAPTER, CLASS, QUESTIONS, SUBJECT, TAG_COLLECTION,
                              app, classify_db, questions_db)
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.classify import Chapters_DB, Class_DB, Subjects_DB
from models.define.classify import ClassifyOwnerType
from models.request.classify import DATA_Create_Chapter, DATA_Create_Class, DATA_Create_Subject, DATA_Delete_Chapter, DATA_Delete_Class, DATA_Delete_Subject, DATA_Group_Create_Subject, DATA_Update_Subject, DATA_Update_chapter, DATA_Update_class

from starlette.responses import JSONResponse


#========================================================
#=================USER_CREATE_SUBJECT====================
#========================================================
@app.post(
    path='/create_subject',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def create_subject(
    data1: DATA_Create_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        subject_data = Subjects_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'subject_id': str(subject_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=================GROUP_CREATE_SUBJECT===================
#========================================================
@app.post(
    path='/group_create_subject',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify - group']
)
async def group_create_subject(
    data1: DATA_Group_Create_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        # check member of group
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=data1.group_id):
            raise Exception('user is not member of group!!!')

        subject_data = Subjects_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            group_id=data1.group_id,
            owner_type=ClassifyOwnerType.GROUP,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'subject_id': str(subject_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#===============COMMUNITY_CREATE_SUBJECT=================
#========================================================
@app.post(
    path='/community_create_subject',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify - community']
)
async def community_create_subject(
    data1: DATA_Create_Subject,
    data2: dict = Depends(valid_headers)
):
    try:
        # check is admin
        if not check_is_admin(user_id=data2.get('user_id')):
            raise Exception('user is not admin!!!')

        subject_data = Subjects_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            owner_type=ClassifyOwnerType.COMMUNITY,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        subject_id = classify_db[SUBJECT].insert_one(jsonable_encoder(subject_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'subject_id': str(subject_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#=======================CREATE_CLASS=====================
#========================================================
@app.post(
    path='/create_class',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def create_class(
    data1: DATA_Create_Class,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of subject
        if not check_permission_with_subject(user_id=data2.get('user_id'), subject_id=data1.subject_id):
            raise Exception('user not have permission with subject!')

        class_data = Class_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            subject_id=data1.subject_id,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        class_id = classify_db[CLASS].insert_one(jsonable_encoder(class_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'class_id': str(class_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#======================CREATE_CHAPTER====================
#========================================================
@app.post(
    path='/create_chapter',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['classify']
)
async def create_chapter(
    data1: DATA_Create_Chapter,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of class
        if not check_permission_with_class(user_id=data2.get('user_id'), class_id=data1.class_id):
            raise Exception('user not have permission with class!')
        
        chapter_data = Chapters_DB(
            name=data1.name,
            user_id=data2.get('user_id'),
            class_id=data1.class_id,
            datetime_created=datetime.now().timestamp()
        )

        #insert into subjects db
        chapter_id = classify_db[CHAPTER].insert_one(jsonable_encoder(chapter_data)).inserted_id
        return JSONResponse(content={'status': 'success', 'data': {'chapter_id': str(chapter_id)}},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


