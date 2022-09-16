from app.utils.account_utils.user import check_is_admin
from app.utils.exam_utils.exam_check_permission import check_owner_of_exam
from app.utils.question_utils.question_check_permission import check_owner_of_question
from configs.settings import COMMUNITY_EXAMS, COMMUNITY_QUESTIONS, GROUP_EXAMS, GROUP_QUESTIONS

from fastapi import Depends, status
from fastapi.responses import JSONResponse

from configs import GROUP, GROUP_PARTICIPANT, app, group_db
from models.request.community import DATA_Remove_Community_Exam, DATA_Remove_Community_Question
from models.request.group import DATA_Remove_Group_Exam, DATA_Remove_Group_Question
# import response models
from models.response import *

# Config logging
from configs.logger import logger
from app.utils._header import valid_headers



#=================================================================
#==================USER_REMOVE_COMMUNITY_QUESTION=================
#=================================================================
@app.delete(
    '/remove_community_question',
    description='user remove community question',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': RemoveMemberResponse404,
        },
        status.HTTP_403_FORBIDDEN: {
            'model': RemoveMemberResponse403,
        },
        status.HTTP_200_OK: {
            'model': RemoveMemberResponse200,
        }
    },
    tags=['Community']
)
async def remove_community_question(
    data: DATA_Remove_Community_Question,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============user_remove_community_question=================')
    try:
        # check is admin
        if check_is_admin(user_id=data2.get('user_id')):
            query_delete = {
                'group_id': data.group_id,
                'question_id': {
                    '$in': data.question_ids
                }
            }
            group_db[COMMUNITY_QUESTIONS].delete_many(query_delete)
        # check member of group
        else:
            query_delete = {
                'question_id': {
                    '$in': data.question_ids
                },
                'sharer_id': data2.get('user_id')
            }
            group_db[COMMUNITY_QUESTIONS].delete_many(query_delete)

        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)

        # # check permission remove community question
        # # check is admin or owner of question
        # if not (check_is_admin(user_id=data2.get('user_id')) or check_owner_of_question(user_id=data2.get('user_id'), question_id=data.question_id)):
        #     raise Exception('Người dùng không có quyền xóa câu hỏi!')

        # group_db[COMMUNITY_QUESTIONS].delete_one(
        #     {
        #         'question_id': data.question_id
        #     }
        # )

        # return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)      
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


#=================================================================
#====================USER_REMOVE_COMMUNITY_EXAM===================
#=================================================================
@app.delete(
    '/remove_community_exam',
    description='user remove community question',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': RemoveMemberResponse404,
        },
        status.HTTP_403_FORBIDDEN: {
            'model': RemoveMemberResponse403,
        },
        status.HTTP_200_OK: {
            'model': RemoveMemberResponse200,
        }
    },
    tags=['Community']
)
async def remove_community_exam(
    data: DATA_Remove_Community_Exam,
    data2: dict = Depends(valid_headers),
):
    logger().info('===============user_remove_community_exam=================')
    try:
        # check is admin
        if check_is_admin(user_id=data2.get('user_id')):
            query_delete = {
                'exam_id': {
                    '$in': data.exam_ids
                }
            }
            group_db[COMMUNITY_EXAMS].delete_many(query_delete)
        # check member of group
        else:
            query_delete = {
                'exam_id': {
                    '$in': data.exam_ids
                },
                'sharer_id': data2.get('user_id')
            }
            group_db[COMMUNITY_EXAMS].delete_many(query_delete)

        return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)

        # # check permission remove community exam
        # # check is admin or owner of exam
        # if not (check_is_admin(user_id=data2.get('user_id')) or check_owner_of_exam(user_id=data2.get('user_id'), exam_id=data.exam_id)):
        #     raise Exception('Người dùng không có quyền xóa đề thi!')

        # group_db[COMMUNITY_EXAMS].delete_one(
        #     {
        #         'exam_id': data.exam_id
        #     }
        # )

        # return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)           
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed', 'msg': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
