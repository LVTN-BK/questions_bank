from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from app.utils.group_utils.group import check_group_exist, check_owner_or_user_of_group, get_list_group_exam
from app.utils.question_utils.question import get_answer, get_data_and_metadata, get_list_tag_id_from_input, get_question_information_with_version_id
from bson import ObjectId
from configs.logger import logger
from configs.settings import COMMUNITY_EXAMS, EXAMS, EXAMS_SECTION, EXAMS_VERSION, GROUP_EXAMS, SYSTEM, app, exams_db, group_db
from fastapi import Depends, Path, Query, status
from fastapi.encoders import jsonable_encoder
from models.db.exam import Exam_Section_DB, Exams_DB, Exams_Version_DB
from models.request.exam import DATA_Create_Exam, DATA_Delete_Exam, DATA_Update_Exam
from starlette.responses import JSONResponse

from models.response.exam import UserGetAllExamResponse200, UserGetAllExamResponse403, UserGetOneExamResponse200, UserGetOneExamResponse403
import random

#========================================================
#=====================CREATE_EXAM========================
#========================================================
@app.post(
    path='/create_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ''
        }
    },
    tags=['exams']
)
async def create_exam(
    data1: DATA_Create_Exam,
    data2: dict = Depends(valid_headers)
):
    try:
        data1 = jsonable_encoder(data1)
        if data1.get('num_version')>1:
            if len(data1.get('exam_codes')) != data1.get('num_version'):
                raise Exception('Số lượng mã đề không đúng!')
        
        exam = Exams_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            tag_id=get_list_tag_id_from_input(data1.get('tag_id')),
            datetime_created=datetime.now().timestamp()
        )

        logger().info(f'exam: {exam}')

        # insert to exams table
        id_exam = exams_db[EXAMS].insert_one(jsonable_encoder(exam)).inserted_id

        for i in range(1, data1.get('num_version') + 1):
            logger().info(data1['questions'])
            # insert section
            questions = []
            for section in data1['questions']:
                exam_section_data = Exam_Section_DB(
                    section_name=section.get('section_name'),
                    section_questions=section.get('section_questions'),
                    user_id=data2.get('user_id'),
                    exam_id=str(id_exam),
                    datetime_created=datetime.now().timestamp()
                )
                id_exam_section = exams_db[EXAMS_SECTION].insert_one(jsonable_encoder(exam_section_data)).inserted_id
                questions.append(str(id_exam_section))
            
            
            # insert exam version to exams_version
            exams_version = Exams_Version_DB(
                exam_id=str(id_exam),
                exam_code=data1.get('exam_codes')[i - 1] if data1.get('exam_codes') else None,
                exam_title=data1.get('exam_title'),
                version_name = i,
                is_latest=False,
                note=data1.get('note'),
                time_limit=data1.get('time_limit'),
                organization_info=data1.get('organization_info'),
                exam_info=data1.get('exam_info'),
                questions=questions,
                datetime_created=datetime.now().timestamp()
            )
            id_exam_version = exams_db[EXAMS_VERSION].insert_one(jsonable_encoder(exams_version)).inserted_id

            # shuffer
            for x in data1['questions']:
                random.shuffle(x['section_questions'])

        # update latest version
        exams_db[EXAMS_VERSION].update_one(
            {
                '_id': id_exam_version
            },
            {
                '$set': {
                    'is_latest': True
                }
            }
        )

        exam = jsonable_encoder(exam)
        exams_version = jsonable_encoder(exams_version)
        exam['exam_version_id'] = str(id_exam_version)
        exam.update({'exam_info': exams_version})

        return JSONResponse(content={'status': 'success', 'data': exam},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#========================UPDATE_EXAM=====================
#========================================================
@app.put(
    path='/update_exam',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ''
        }
    },
    tags=['exams']
)
async def update_exam(
    data1: DATA_Update_Exam,
    data2: dict = Depends(valid_headers)
):
    try:
        # check owner of question
        data1 = jsonable_encoder(data1)
        query_exam = {}
        if data1.get('class_id'):
            query_class = {
                'class_id': data1.get('class_id')
            }
            query_exam.update(query_class)
        if data1.get('subject_id'):
            query_subject = {
                'subject_id': data1.get('subject_id')
            }
            query_exam.update(query_subject)
        
        if data1.get('tag_id'):
            query_tag = {
                'tag_id': get_list_tag_id_from_input(data1.get('tag_id'))
            }
            query_exam.update(query_tag)
        
        query_exam.update(
            {
                'datetime_updated': datetime.now().timestamp()
            }
        )
        
        # find version of exam
        exam_version_info = exams_db[EXAMS_VERSION].find_one({
            '_id': ObjectId(data1.get('exam_version_id')),
        })
        if not exam_version_info:
            msg = 'exam version not found!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        

        # update question collection
        update_exam = exams_db[EXAMS].find_one_and_update(
            {
                '_id': ObjectId(exam_version_info.get('exam_id')),
                'user_id': data2.get('user_id')
            },
            {
                '$set': query_exam
            }
        )
        if not update_exam:
            msg = 'not your exam!'
            return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        query_exam_version = {}
        if data1.get('exam_title') and data1.get('exam_title') != exam_version_info.get('exam_title'):
            query_exam_title = {
                'exam_title': data1.get('exam_title')
            }
            query_exam_version.update(query_exam_title)
        if data1.get('exam_code') and data1.get('exam_code') != exam_version_info.get('exam_code'):
            query_exam_code = {
                'exam_code': data1.get('exam_code')
            }
            query_exam_version.update(query_exam_code)
        if data1.get('note') and data1.get('note') != exam_version_info.get('note'):
            query_note = {
                'note': data1.get('note')
            }
            query_exam_version.update(query_note)
        if data1.get('time_limit') and data1.get('time_limit') != exam_version_info.get('time_limit'):
            query_time_limit = {
                'time_limit': data1.get('time_limit')
            }
            query_exam_version.update(query_time_limit)
        if data1.get('organization_info') and data1.get('organization_info') != exam_version_info.get('organization_info'):
            query_organization_info = {
                'organization_info': data1.get('organization_info')
            }
            query_exam_version.update(query_organization_info)
        if data1.get('exam_info') and data1.get('exam_info') != exam_version_info.get('exam_info'):
            query_exam_info = {
                'exam_info': data1.get('exam_info')
            }
            query_exam_version.update(query_exam_info)
        # if data1.get('questions') and data1.get('questions') != exam_version_info.get('questions'):
        #     query_questions = {
        #         'questions': data1.get('questions')
        #     }
        #     query_exam_version.update(query_questions)

        if data1.get('new_version'):
            # insert section
            questions = []
            for section in data1['questions']:
                exam_section_data = Exam_Section_DB(
                    section_name=section.get('section_name'),
                    section_questions=section.get('section_questions'),
                    user_id=data2.get('user_id'),
                    exam_id=exam_version_info.get('exam_id'),
                    datetime_created=datetime.now().timestamp()
                )
                id_exam_section = exams_db[EXAMS_SECTION].insert_one(jsonable_encoder(exam_section_data)).inserted_id
                questions.append(str(id_exam_section))

            # update older version status
            up_exam_version = exams_db[EXAMS_VERSION].find_one_and_update({
                'exam_id': exam_version_info.get('exam_id'),
                'is_latest': True
            },
            {
                '$set': {
                    'is_latest': False
                }
            })

            # insert new version
            query_version_name = {
                'version_name': up_exam_version.get('version_name') + 1,
                'questions': questions,
                'datetime_created': datetime.now().timestamp()
            }
            query_exam_version.update(query_version_name)

            del exam_version_info['_id']
            exam_version_info.update(query_exam_version)
            exam_version_info = exams_db[EXAMS_VERSION].insert_one(exam_version_info)
        else:
            # check len questions section
            new_questions = []
            for i in range(len(data1.get('questions'))):
                data_section_update = data1.get('questions')[i]
                if len(exam_version_info.get('questions'))>i:
                    exams_db[EXAMS_SECTION].find_one_and_update(
                        {
                            '_id': ObjectId(exam_version_info["questions"][i])
                        },
                        {
                            '$set': data_section_update
                        }
                    )
                    new_questions.append(exam_version_info["questions"][i])
                else:
                    exam_section_data = Exam_Section_DB(
                        section_name=data_section_update.get('section_name'),
                        section_questions=data_section_update.get('section_questions'),
                        user_id=data2.get('user_id'),
                        exam_id=exam_version_info.get('exam_id'),
                        datetime_created=datetime.now().timestamp()
                    )
                    id_exam_section = exams_db[EXAMS_SECTION].insert_one(jsonable_encoder(exam_section_data)).inserted_id
                    new_questions.append(str(id_exam_section))
            # update version
            query_version_name = {
                'questions': new_questions,
                'datetime_created': datetime.now().timestamp()
            }
            query_exam_version.update(query_version_name)

            del exam_version_info['_id']
            exam_version_info.update(query_exam_version)
            exam_version_info = exams_db[EXAMS_VERSION].update_one(
                {
                    '_id': ObjectId(data1.get('exam_version_id')),
                },
                {
                    '$set': exam_version_info
                }
            )

        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


#========================================================
#=======================DELETE_EXAMS=====================
#========================================================
@app.delete(
    path='/delete_exams',
    responses={
        status.HTTP_200_OK: {
            'model': ''
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ''
        }
    },
    tags=['exams']
)
async def delete_exams(
    data: DATA_Delete_Exam,
    data2: dict = Depends(valid_headers)
):
    try:
        all_id = []
        # find question
        for exam_id in data.list_exam_ids:
            exam_del = exams_db[EXAMS].find_one_and_update(
                {
                    "_id": ObjectId(exam_id),
                    'user_id': data2.get('user_id')       
                },
                {
                    '$set': {
                        'is_removed': True
                    }
                }
            )

            if exam_del:
                all_id.append(exam_id)
        
                # # find exam version
                # exam_version = exams_db[EXAMS_VERSION].delete_many(
                #     {
                #         'exam_id': exam_id
                #     }
                # )
        # delete exam in group
        exams_db[GROUP_EXAMS].delete_many(
            {
                'exam_id': {
                    '$in': all_id
                }
            }
        )

        # delete exam in community
        exams_db[COMMUNITY_EXAMS].delete_many(
            {
                'exam_id': {
                    '$in': all_id
                }
            }
        )

        return JSONResponse(content={'status': 'success'},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)



