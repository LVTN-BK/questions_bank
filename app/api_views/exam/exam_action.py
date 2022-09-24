import pandas as pd
from typing import List
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.classify_utils.classify import get_community_classify_other_id, get_group_classify_other_id, get_subject_info
from app.utils.exam_utils.exam_check_permission import check_owner_of_exam, check_owner_of_exam_version
from app.utils.exam_utils.exam_eval import evaluate_irt, get_item_level_name, get_probability_irt, insert_exam_evaluate, insert_question_evaluate
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_question
from app.utils.question_utils.question import get_question_level, question_evaluation_func
from app.utils.question_utils.question_check_permission import check_owner_of_question
from bson import ObjectId
from configs.logger import logger
from configs.settings import (COMMUNITY_EXAMS, EXAMS_CONFIG, EXAMS_EVALUATION, EXAMS_VERSION, exams_db, EXAMS, GROUP_EXAMS, GROUP_QUESTIONS, QUESTIONS, QUESTIONS_EVALUATION, QUESTIONS_VERSION, SYSTEM,
                              app, questions_db, group_db)
from fastapi import Depends, status, BackgroundTasks, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from models.db.community import CommunityExam
from models.db.exam import Exam_Config_DB, Exams_DB, Exams_Version_DB
from models.db.group import GroupExam
from models.db.question import Questions_DB, Questions_Version_DB
from models.define.decorator_api import SendNotiDecoratorsApi
from models.define.exam import ManageExamEvaluationStatus
from models.request.exam import DATA_Copy_Exam, DATA_Copy_Exam_By_Version, DATA_Evaluate_Exam, DATA_Save_Exam_Config, DATA_Share_Exam_To_Community, DATA_Share_Exam_To_Group
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
    exam_id: str = Form(...),
    exam_version_id: str = Form(...),
    file: UploadFile = File(...,description="file as UploadFile"),
    data2: dict = Depends(valid_headers)
):
    try:
        # contents = file.file.read()
        # from io import StringIO
        # s = str(contents,'utf-8')
        # data_excel = StringIO(s)
        df = pd.read_excel(file.file.read())
        file.file.close()
        num_row = df.shape[0]
        num_col = df.shape[1]
        logger().info(num_col)

        # add column name "total" to sum add point for each student
        df['total'] =  df[list(df.columns)].sum(axis=1)
        
        # list difficult param for each group same ability
        list_b_total = []

        # list ability params for group same ability
        list_a_total = []

        for x in df.groupby("total"):   # group by same point/same ability
            # get dataFrame for each group
            dfx = x[1]
            dfx = dfx.drop(['total'], axis=1)

            # num student in group
            size = dfx.shape[0]

            # list probability answer right
            list_p = [get_probability_irt(sum=sum, size=size, n=num_row) for sum in dfx.sum()]
            
            # list evaluation value
            list_e = [evaluate_irt(p) for p in list_p]

            # ability value of group same ability
            a = sum(list_e)/len(list_e)

            list_a_total.append(a)
            
            # danh sach do kho cau hoi cua nhom nang luc k
            list_b = [(a-e) for e in list_e]

            list_b_total.append(list_b)
            
        df = df.drop(['total'], axis=1)

        # get list difficult param
        df_group = pd.DataFrame(list_b_total, columns =list(df.columns))
        size_group = df_group.shape[0]
        list_difficult_param = [v/size_group for v in df_group.sum()]

        # nang luc trung binh
        a_mean = sum(list_a_total)/len(list_a_total)

        # danh sach xac suat tra loi dung cau hoi
        list_probability_all = [s/num_row for s in df.sum()]

        # # insert data to database
        # background_tasks.add_task(
        #     insert_question_evaluate, 
        #     user_id = data2.get('user_id'),
        #     question_ids = list(df.columns), 
        #     difficult_params = list_difficult_param, 
        #     probabilities = list_probability_all, 
        #     ability = a_mean,
        #     num_student = num_row
        # )

        # return data:
        list_questions = list(df.columns)

        question_eval_data = []
        for x in range(num_col):
            data_eval = {
                'question_id': list_questions[x],
                'correct_probability': round(list_probability_all[x], 3),
                'num_student': num_row,
                'difficult_value': round(list_difficult_param[x], 3),
                'old_level': get_question_level(question_id=list_questions[x]),
                'result': get_item_level_name(b = list_difficult_param[x]),
                'status': ManageExamEvaluationStatus.PENDING
            }
            question_eval_data.append(data_eval)
        
        result_data = {
            'exam_id': exam_id,
            'datetime_created': datetime.now().timestamp(),
            'data': question_eval_data
        }

        data_insert_exam = {
            'user_id': data2.get('user_id'),
            'exam_id': exam_id,
            'exam_version_id': exam_version_id,
            'datetime_created': result_data.get('datetime_created')
        }
        # insert evaluation into db
        insert_exam_id = exams_db[EXAMS_EVALUATION].insert_one(data_insert_exam).inserted_id
        
        result_data.update(
            {
                'id': str(insert_exam_id)
            }
        )

        # insert data to database
        background_tasks.add_task(
            insert_exam_evaluate, 
            user_id = data2.get('user_id'),
            # evaluation_id = str(insert_exam_id), 
            data = result_data
        )

        return JSONResponse(content={'status': 'success', 'data': result_data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


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
    tags=['exams - action']
)
async def copy_exam(
    background_tasks: BackgroundTasks,
    data: DATA_Copy_Exam,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        if check_owner_of_exam(user_id=data2.get('user_id'), exam_id=data.exam_id):
            raise Exception('user is now owner of exam!!!')

        # find exam info
        exam_info = exams_db[EXAMS].find_one(
            {
                '_id': ObjectId(data.exam_id),
            }
        )

        # find exam latest version
        exam_version_info = exams_db[EXAMS_VERSION].find_one(
            {
                'exam_id': data.exam_id,
                'is_latest': True
            }
        )

        if not exam_info or not exam_version_info:
            raise Exception('exam not found!!!')

        exam_data = Exams_DB(
            user_id=data2.get('user_id'),
            class_id=data.class_id,
            subject_id=data.subject_id,
            tag_id=exam_info.get('tag_id'),
            datetime_created=datetime.now().timestamp()
        )
        exam_insert_id = exams_db[EXAMS].insert_one(jsonable_encoder(exam_data)).inserted_id

        
        exam_version_data = Exams_Version_DB(
            exam_id=str(exam_insert_id),
            exam_title=exam_version_info.get('exam_title'),
            note=exam_version_info.get('note'),
            time_limit=exam_version_info.get('time_limit'),
            organization_info=exam_version_info.get('organization_info'),
            exam_info=exam_version_info.get('exam_info'),
            questions=exam_version_info.get('questions'),
            datetime_created=datetime.now().timestamp()
        )

        exams_db[EXAMS_VERSION].insert_one(jsonable_encoder(exam_version_data))

        data = {
            'exam_id': str(exam_insert_id)
        }

        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#==================EXAMS_COPY_BY_VERSION=================
#========================================================
@app.post(
    path='/copy_exam_by_version',
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
async def copy_exam_by_version(
    background_tasks: BackgroundTasks,
    data: DATA_Copy_Exam_By_Version,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of exam version
        if check_owner_of_exam_version(user_id=data2.get('user_id'), exam_version_id=data.exam_version_id):
            raise Exception('user is now owner of exam!!!')

        # find exam version info
        exam_version_info = exams_db[EXAMS_VERSION].find_one(
            {
                '_id': ObjectId(data.exam_version_id),
            }
        )

        # find exam info
        exam_info = exams_db[EXAMS].find_one(
            {
                '_id': ObjectId(exam_version_info.get('exam_id')),
            }
        )


        if not exam_info or not exam_version_info:
            raise Exception('exam not found!!!')

        exam_data = Exams_DB(
            user_id=data2.get('user_id'),
            class_id=data.class_id,
            subject_id=data.subject_id,
            tag_id=exam_info.get('tag_id'),
            datetime_created=datetime.now().timestamp()
        )
        exam_insert_id = exams_db[EXAMS].insert_one(jsonable_encoder(exam_data)).inserted_id

        
        exam_version_data = Exams_Version_DB(
            exam_id=str(exam_insert_id),
            exam_title=exam_version_info.get('exam_title'),
            note=exam_version_info.get('note'),
            time_limit=exam_version_info.get('time_limit'),
            organization_info=exam_version_info.get('organization_info'),
            exam_info=exam_version_info.get('exam_info'),
            questions=exam_version_info.get('questions'),
            datetime_created=datetime.now().timestamp()
        )

        exam_version_insert_id = exams_db[EXAMS_VERSION].insert_one(jsonable_encoder(exam_version_data)).inserted_id

        data = {
            'exam_id': str(exam_insert_id),
            'exam_version_id': str(exam_version_insert_id)
        }

        return JSONResponse(content={'status': 'success', 'data': data},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

#========================================================
#=====================SAVE_EXAM_CONFIG===================
#========================================================
@app.post(
    path='/save_exam_config',
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
async def save_exam_config(
    background_tasks: BackgroundTasks,
    data: DATA_Save_Exam_Config,
    data2: dict = Depends(valid_headers)
):
    try:
        data_config = Exam_Config_DB(
            user_id=data2.get('user_id'),
            name=data.name,
            data=data.data,
            datetime_created=datetime.now().timestamp()
        )
        # find exam version info
        exam_version_info = exams_db[EXAMS_CONFIG].insert_one(jsonable_encoder(data_config))

        
        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


