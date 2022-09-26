import copy
import json
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_chapter_info, get_class_info, get_community_classify_other_id, get_group_classify_other_id, get_subject_info
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_data_and_metadata, get_list_tag_id_from_input, get_query_filter_questions, get_question_evaluation_value, question_import_func, reject_update_question_evaluation_status, update_question_evaluation_status
from app.utils.question_utils.question_check_permission import check_owner_of_question, check_owner_of_question_version
from bson import ObjectId
from configs.logger import logger
from configs.settings import (ANSWERS, COMMUNITY_QUESTIONS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, Path, Query, status, BackgroundTasks, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from models.db.community import CommunityQuestion
from models.db.group import GroupQuestion
from models.db.question import Answers_DB, Questions_DB, Questions_Evaluation_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.question import ManageQuestionType
from models.request.question import (DATA_Copy_Question, DATA_Copy_Question_By_Version, DATA_Create_Answer,
                                     DATA_Create_Fill_Question,
                                     DATA_Create_Matching_Question,
                                     DATA_Create_Multi_Choice_Question,
                                     DATA_Create_Sort_Question, DATA_Delete_Question, DATA_Evaluate_Question, DATA_Import_Question, DATA_Reject_Update_Question_Level, DATA_Share_Question_To_Community, DATA_Share_Question_To_Group, DATA_Update_Question, DATA_Update_Question_Classify, DATA_Update_Question_Level)
from starlette.responses import JSONResponse




#========================================================
#=====================QUESTIONS_SHARE====================
#========================================================
@app.post(
    path='/share_question_to_community',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - share']
)
async def share_question_to_community(
    background_tasks: BackgroundTasks,
    data: DATA_Share_Question_To_Community,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        if not check_owner_of_question(user_id=data2.get('user_id'), question_id=data.question_id):
            raise Exception('user is not owner of question!!!')

        # check classify
        if not all([data.subject_id, data.class_id, data.chapter_id]):
            data.subject_id, data.class_id, data.chapter_id = get_community_classify_other_id(user_id=data2.get('user_id'))
        else: # check is community classify
            pass
            ########################
            ########################
            ########################
        
        # add question to community:
        community_question = CommunityQuestion(
            question_id=data.question_id,
            sharer_id=data2.get('user_id'),
            subject_id=data.subject_id,
            class_id=data.class_id,
            chapter_id=data.chapter_id,
            datetime_created=datetime.now().timestamp()
        )
        
        insert = group_db[COMMUNITY_QUESTIONS].insert_one(jsonable_encoder(community_question))

        # # update question:
        # check = questions_db[QUESTIONS].update_one(
        #     {
        #         '_id': ObjectId(data.question_id)
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
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#=====================QUESTIONS_SHARE====================
#========================================================
@app.post(
    path='/share_question_to_group',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - share']
)
@SendNotiDecoratorsApi.group_share_question
async def share_question_to_group(
    background_tasks: BackgroundTasks,
    data: DATA_Share_Question_To_Group,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        if not check_owner_of_question(user_id=data2.get('user_id'), question_id=data.question_id):
            raise Exception('user is not owner of question!!!')

        #check group exist:
        if not check_group_exist(group_id=data.group_id):
            msg = 'group not found!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)

        # check member of group
        if not check_owner_or_user_of_group(user_id=data2.get('user_id'), group_id=data.group_id):
            raise Exception('user is not member of group!!!')

        # check classify
        if not all([data.subject_id, data.class_id, data.chapter_id]):
            data.subject_id, data.class_id, data.chapter_id = get_group_classify_other_id(group_id=data.group_id, user_id=data2.get('user_id'))
        else: # check is group classify
            pass
            ########################
            ########################
            ########################
        
        # add question to group:
        group_question = GroupQuestion(
            group_id=data.group_id,
            question_id=data.question_id,
            sharer_id=data2.get('user_id'),
            subject_id=data.subject_id,
            class_id=data.class_id,
            chapter_id=data.chapter_id,
            datetime_created=datetime.now().timestamp()
        )
        
        insert = group_db[GROUP_QUESTIONS].insert_one(jsonable_encoder(group_question))

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'Failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#======================EVALUATE_QUESTION=================
#========================================================
@app.post(
    path='/evaluate_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions']
)
async def evaluate_question(
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
#=====================QUESTIONS_COPY=====================
#========================================================
@app.post(
    path='/copy_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def copy_question(
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
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=================QUESTIONS_COPY_BY_VERSION==============
#========================================================
@app.post(
    path='/copy_question_by_version',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def copy_question_by_version(
    # background_tasks: BackgroundTasks,
    data: DATA_Copy_Question_By_Version,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question version
        if check_owner_of_question_version(user_id=data2.get('user_id'), question_version_id=data.question_version_id):
            raise Exception('user is now owner of question!!!')

        # find question version info
        question_version_info = questions_db[QUESTIONS_VERSION].find_one(
            {
                '_id': ObjectId(data.question_version_id)
            }
        )

        # find question info
        question_info = questions_db[QUESTIONS].find_one(
            {
                '_id': ObjectId(question_version_info.get('question_id')),
            }
        )

        

        if not question_info or not question_version_info:
            raise Exception('question not found!!!')

        
        question_info.update(
            {
                'user_id':data2.get('user_id'),
                'class_id':data.class_id,
                'subject_id':data.subject_id,
                'chapter_id':data.chapter_id,
                'datetime_created':datetime.now().timestamp()
            }
        )
        del question_info['_id']

        # question_data = Questions_DB(
        #     user_id=data2.get('user_id'),
        #     class_id=data.class_id,
        #     subject_id=data.subject_id,
        #     chapter_id=data.chapter_id,
        #     type=question_info.get('type'),
        #     tag_id=question_info.get('tag_id'),
        #     level=question_info.get('level'),
        #     datetime_created=datetime.now().timestamp()
        # )
        question_insert_id = questions_db[QUESTIONS].insert_one(question_info).inserted_id
        # question_insert_id = questions_db[QUESTIONS].insert_one(jsonable_encoder(question_data)).inserted_id

        
        # question_version_data = Questions_Version_DB(
        #     question_id=str(question_insert_id),
        #     question_content=question_version_info.get('question_content'),
        #     answers=question_version_info.get('answers'),
        #     answers_right=question_version_info.get('answers_right'),
        #     sample_answer=question_version_info.get('sample_answer'),
        #     display=question_version_info.get('display'),
        #     datetime_created=datetime.now().timestamp()
        # )
        question_version_info.update(
            {
                'question_id':str(question_insert_id),
                'version_name': 1,
                'is_latest': True,
                'datetime_created':datetime.now().timestamp()
            }
        )
        del question_version_info['_id']

        question_version_insert_id = questions_db[QUESTIONS_VERSION].insert_one(question_version_info).inserted_id
        # question_version_insert_id = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(question_version_data)).inserted_id

        data = {
            'question_id': str(question_insert_id),
            'question_version_id': str(question_version_insert_id)
        }

        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#====================QUESTIONS_IMPORT====================
#========================================================
@app.post(
    path='/import_question',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def import_question(
    background_tasks: BackgroundTasks,
    data: DATA_Import_Question = Depends(),
    file: UploadFile= File(...,description="file as UploadFile"),
    data2: dict = Depends(valid_headers)
):
    try:
        list_question_data = json.load(file.file)
        for question_data in list_question_data:
            question_import_func(data=data, question_data=question_data, user_id=data2.get('user_id'))
            # background_tasks.add_task(question_import_func, data=data, question_data=question_data, user_id=data2.get('user_id'))

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#====================UPDATE_QUESTION_LEVEL===============
#========================================================
@app.put(
    path='/accept_update_question_level',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def accept_update_question_level(
    background_tasks: BackgroundTasks,
    data: DATA_Update_Question_Level,
    data2: dict = Depends(valid_headers)
):
    try:
        for question_id in data.question_ids:
            # find question evaluation
            ques_eval = questions_db[QUESTIONS_EVALUATION].find_one(
                {
                    'question_id': question_id,
                    'user_id': data2.get('user_id'),
                    'evaluation_id': data.evaluation_id
                }
            )
            logger().info(ques_eval)
            if ques_eval:
                query_question = {
                    'level': ques_eval.get('result'),
                    'datetime_updated': datetime.now().timestamp()
                }

                # update question collection
                update_question = questions_db[QUESTIONS].find_one_and_update(
                    {
                        '_id': ObjectId(question_id),
                        'user_id': data2.get('user_id')
                    },
                    {
                        '$set': query_question
                    }
                )
        
        # update question evaluation
        background_tasks.add_task(
            update_question_evaluation_status, 
            user_id = data2.get('user_id'),
            data = data
        )
            
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#================REJECT_UPDATE_QUESTION_LEVEL============
#========================================================
@app.put(
    path='/reject_update_question_level',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def reject_update_question_level(
    background_tasks: BackgroundTasks,
    data: DATA_Reject_Update_Question_Level,
    data2: dict = Depends(valid_headers)
):
    try:
        # update question evaluation
        background_tasks.add_task(
            reject_update_question_evaluation_status, 
            user_id = data2.get('user_id'),
            data = data
        )
            
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#===================UPDATE_QUESTION_CLASSIFY=============
#========================================================
@app.post(
    path='/update_question_classify',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['questions - action']
)
async def update_question_classify(
    data: DATA_Update_Question_Classify,
    data2: dict = Depends(valid_headers)
):
    try:
        list_object_id = [ObjectId(x) for x in data.question_ids]
        questions_db[QUESTIONS].update_many(
            {
                '_id': {
                    '$in': list_object_id
                },
                'user_id': data2.get('user_id')
            },
            {
                '$set': {
                    'subject_id': data.subject_id,
                    'class_id': data.class_id,
                    'chapter_id': data.chapter_id
                }
            }
        )
        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

