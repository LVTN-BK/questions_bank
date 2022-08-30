import copy
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_chapter_info, get_class_info, get_subject_info
from app.utils.exam_utils.exam_check_permission import check_owner_of_exam
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from configs.logger import logger
from configs.settings import (ANSWERS, GROUP_EXAMS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, Path, Query, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from models.db.group import GroupExam, GroupQuestion
from models.db.question import Answers_DB, Questions_DB, Questions_Evaluation_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.question import ManageQuestionType
from models.request.exam import DATA_Share_Exam_To_Group
from models.request.question import (DATA_Copy_Question, DATA_Create_Answer,
                                     DATA_Create_Fill_Question,
                                     DATA_Create_Matching_Question,
                                     DATA_Create_Multi_Choice_Question,
                                     DATA_Create_Sort_Question, DATA_Delete_Question, DATA_Evaluate_Question, DATA_Share_Question_To_Community, DATA_Share_Question_To_Group, DATA_Update_Question)
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
    tags=['questions - share'],
    deprecated=True
)
async def share_exam_to_community(
    background_tasks: BackgroundTasks,
    data: DATA_Share_Question_To_Community,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        if not check_owner_of_question(user_id=data2.get('user_id'), question_id=data.question_id):
            raise Exception('user is not owner of question!!!')

        # update question:
        check = questions_db[QUESTIONS].update_one(
            {
                '_id': ObjectId(data.question_id)
            },
            {
                '$set': {
                    'is_public': True
                }
            }
        )

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
    tags=['exams - share']
)
# @SendNotiDecoratorsApi.group_share_question
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

        # add exam to group:
        group_exam = GroupExam(
            group_id=data.group_id,
            exam_id=data.exam_id,
            sharer_id=data2.get('user_id'),
            datetime_created=datetime.now().timestamp()
        )
        
        insert = group_db[GROUP_EXAMS].insert_one(jsonable_encoder(group_exam))

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


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
    tags=['exams'],
    deprecated=True
)
async def evaluate_exam(
    data: DATA_Evaluate_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        recommend_level = get_question_evaluation_value(
            num_correct=data.num_correct,
            num_incorrect=data.num_incorrect,
            discrimination=data.discrimination,
            ability=data.ability,
            guessing=data.guessing
        )

        evaluate_question_data = Questions_Evaluation_DB(
            question_id=data.question_id,
            user_id=data2.get('user_id'),
            is_latest=True,
            num_correct=data.num_correct,
            num_incorrect=data.num_incorrect,
            discrimination_param=data.discrimination,
            ability_level=data.ability,
            guessing_param=data.guessing,
            recommend_level=recommend_level,
            datetime_created=datetime.now().timestamp()
        )
        # update current latest question evaluation
        update_question_evaluation = questions_db[QUESTIONS_EVALUATION].find_one_and_update(
            {
                'question_id': data.question_id,
                'user_id': data2.get('user_id'),
                'is_latest': True
            },
            {
                '$set': {
                    'is_latest': False
                }
            }
        )
        
        # insert evaluation into db
        questions_db[QUESTIONS_EVALUATION].insert_one(jsonable_encoder(evaluate_question_data))
        
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

