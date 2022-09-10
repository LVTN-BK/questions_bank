import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_community_classify_other_id, get_group_classify_other_id, get_subject_info
from app.utils.exam_utils.exam_check_permission import check_owner_of_exam
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import question_evaluation_func
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from configs.logger import logger
from configs.settings import (COMMUNITY_EXAMS, exams_db, EXAMS, GROUP_EXAMS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, status, BackgroundTasks, UploadFile, File
from fastapi.encoders import jsonable_encoder
from models.db.community import CommunityExam
from models.db.group import GroupExam
from models.db.question import Questions_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.request.exam import DATA_Evaluate_Exam, DATA_Share_Exam_To_Community, DATA_Share_Exam_To_Group
from models.request.question import (DATA_Copy_Question, DATA_Evaluate_Question)
from starlette.responses import JSONResponse


#========================================================
#=======================EXAMS_SHARE======================
#========================================================
@app.post(
    path='/share_exam_to_community',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - action']
)
async def share_exam_to_community(
    background_tasks: BackgroundTasks,
    data: DATA_Share_Exam_To_Community,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of exam
        if not check_owner_of_exam(user_id=data2.get('user_id'), exam_id=data.exam_id):
            raise Exception('user is not owner of exam!!!')

        # check classify
        if not all([data.subject_id, data.class_id]):
            data.subject_id, data.class_id, _ = get_community_classify_other_id(user_id=data2.get('user_id'))
        else: # check is group classify
            pass
            ########################
            ########################
            ########################

        # add exam to group:
        community_exam = CommunityExam(
            exam_id=data.exam_id,
            sharer_id=data2.get('user_id'),
            subject_id=data.subject_id,
            class_id=data.class_id,
            datetime_created=datetime.now().timestamp()
        )
        
        insert = group_db[COMMUNITY_EXAMS].insert_one(jsonable_encoder(community_exam))
        
        # # update exam:
        # check = exams_db[EXAMS].update_one(
        #     {
        #         '_id': ObjectId(data.exam_id)
        #     },
        #     {
        #         '$set': {
        #             'is_public': True
        #         }
        #     }
        # )

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#=======================EXAMS_SHARE======================
#========================================================
@app.post(
    path='/share_exam_to_group',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - action']
)
@SendNotiDecoratorsApi.group_share_exam
async def share_exam_to_group(
    background_tasks: BackgroundTasks,
    data: DATA_Share_Exam_To_Group,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of exam
        if not check_owner_of_exam(user_id=data2.get('user_id'), exam_id=data.exam_id):
            raise Exception('user is not owner of exam!!!')

        #check group exist:
        if not check_group_exist(group_id=data.group_id):
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # check member of group
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=data.group_id):
            raise Exception('user is not member of group!!!')

        # check classify
        if not all([data.subject_id, data.class_id]):
            data.subject_id, data.class_id, _ = get_group_classify_other_id(group_id=data.group_id, user_id=data2.get('user_id'))
        else: # check is group classify
            pass
            ########################
            ########################
            ########################

        # add exam to group:
        group_exam = GroupExam(
            group_id=data.group_id,
            exam_id=data.exam_id,
            sharer_id=data2.get('user_id'),
            subject_id=data.subject_id,
            class_id=data.class_id,
            datetime_created=datetime.now().timestamp()
        )
        
        insert = group_db[GROUP_EXAMS].insert_one(jsonable_encoder(group_exam))

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#======================EVALUATE_EXAM=====================
#========================================================
@app.post(
    path='/evaluate_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - action']
)
async def evaluate_exam(
    background_tasks: BackgroundTasks,
    data: List[DATA_Evaluate_Question],
    data2: dict = Depends(valid_headers)
):
    try:
        for data_result in data:
            background_tasks.add_task(question_evaluation_func, data=data_result, user_id=data2.get('user_id'))
            # question_evaluation_func(data=data_result, user_id=data2.get('user_id'))
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#==================EVALUATE_EXAM_BY_FILE=================
#========================================================
@app.post(
    path='/evaluate_exam_by_file',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - action']
)
async def evaluate_exam_by_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...,description="file as UploadFile"),
    data2: dict = Depends(valid_headers)
):
    try:
        
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#=======================EXAMS_COPY=======================
#========================================================
@app.post(
    path='/copy_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams - action'],
    deprecated=True
)
async def copy_exam(
    background_tasks: BackgroundTasks,
    data: DATA_Copy_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        if check_owner_of_question(user_id=data2.get('user_id'), question_id=data.question_id):
            raise Exception('user is now owner of question!!!')

        # find question info
        question_info = questions_db[QUESTIONS].find_one(
            {
                '_id': ObjectId(data.question_id),
            }
        )

        # find question latest version
        question_version_info = questions_db[QUESTIONS_VERSION].find_one(
            {
                'question_id': data.question_id,
                'is_latest': True
            }
        )

        if not question_info or not question_version_info:
            raise Exception('question not found!!!')

        question_data = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data.class_id,
            subject_id=data.subject_id,
            chapter_id=data.chapter_id,
            type=question_info.get('type'),
            tag_id=question_info.get('tag_id'),
            level=question_info.get('level'),
            datetime_created=datetime.now().timestamp()
        )
        question_insert_id = questions_db[QUESTIONS].insert_one(jsonable_encoder(question_data)).inserted_id

        
        question_version_data = Questions_Version_DB(
            question_id=str(question_insert_id),
            question_content=question_version_info.get('question_content'),
            answers=question_version_info.get('answers'),
            answers_right=question_version_info.get('answers_right'),
            sample_answer=question_version_info.get('sample_answer'),
            display=question_version_info.get('display'),
            datetime_created=datetime.now().timestamp()
        )

        questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(question_version_data))

        data = {
            'question_id': str(question_insert_id)
        }

        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



def test_pd():
    import pandas as pd

    df = pd.read_csv('Book2.xlsx')

    print(df.to_string()) 
