from fastapi import status, Form
from fastapi import Body, Depends
from app.utils.account import send_reset_password_email
from configs.logger import logger
from models.db.question import Answers_DB, Questions_DB, Questions_Version_DB
from models.define.question import ManageQuestionType
from models.define.user import UserInfo
from models.request.account import DATA_Update_Account, DATA_Update_Email, DATA_Update_Password
from models.request.question import DATA_Create_Answer, DATA_Create_Fill_Question, DATA_Create_Matching_Question, DATA_Create_Multi_Choice_Question, DATA_Create_Sort_Question
from pymongo.collection import ReturnDocument
from starlette.responses import JSONResponse
from configs.settings import QUESTIONS, QUESTIONS_VERSION, SYSTEM, USER_COLLECTION, USERS_PROFILE, app, questions_db
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder


#========================================================
#=============CREATE__MULTI_CHOICE_QUESTION==============
#========================================================
@app.post(
    path='/create_multi_choice_question',
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
async def create_multi_choice_question(
    data1: DATA_Create_Multi_Choice_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # check user
        user = SYSTEM['users'].find_one(
            {
                'email': {
                    '$eq': data2.get('email')
                }
            }
        )
        if not user:
            return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.MULTICHOICE,
            tag_id=data1.get('tag_id'),
            level_id=data1.get('level_id'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=================CREATE_MATCHING_QUESTION===============
#========================================================
@app.post(
    path='/create_matching_question',
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
async def create_matching_question(
    data1: DATA_Create_Matching_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.MATCHING,
            tag_id=data1.get('tag_id'),
            level_id=data1.get('level_id'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#==================CREATE_SORT_QUESTION==================
#========================================================
@app.post(
    path='/create_sort_question',
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
async def create_sort_question(
    data1: DATA_Create_Sort_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.SORT,
            tag_id=data1.get('tag_id'),
            level_id=data1.get('level_id'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#==================CREATE_FILL_QUESTION==================
#========================================================
@app.post(
    path='/create_fill_question',
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
async def create_fill_question(
    data1: DATA_Create_Fill_Question,
    data2: dict = Depends(valid_headers)
):
    try:
        # # check user
        # user = SYSTEM['users'].find_one(
        #     {
        #         'email': {
        #             '$eq': data2.get('email')
        #         }
        #     }
        # )
        # if not user:
        #     return JSONResponse(content={'status': 'User not found or permission deny!'}, status_code=status.HTTP_403_FORBIDDEN)

        data1 = jsonable_encoder(data1)
        
        question = Questions_DB(
            user_id=data2.get('user_id'),
            class_id=data1.get('class_id'),
            subject_id=data1.get('subject_id'),
            chapter_id=data1.get('chapter_id'),
            type=ManageQuestionType.FILL,
            tag_id=data1.get('tag_id'),
            level_id=data1.get('level_id'),
        )

        logger().info(f'question: {question}')

        # insert to questions table
        id_question = questions_db[QUESTIONS].insert_one(jsonable_encoder(question)).inserted_id

        # insert question version to questions_version
        questions_version = Questions_Version_DB(
            question_id=str(id_question),
            question_content=data1.get('question_content'),
            question_image=data1.get('question_image'),
            answers=data1.get('answers'),
            correct_answers=data1.get('correct_answers'),
        )
        id_question_version = questions_db[QUESTIONS_VERSION].insert_one(jsonable_encoder(questions_version)).inserted_id

        question = jsonable_encoder(question)
        questions_version = jsonable_encoder(questions_version)
        question.update({'question_info': questions_version})

        return JSONResponse(content={'status': 'success', 'data': question},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

#========================================================
#=====================CREATE_ANSWER======================
#========================================================
@app.post(
    path='/create_answer',
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
async def create_answer(
    data1: DATA_Create_Answer,
    data2: dict = Depends(valid_headers)
):
    try:
        data1 = jsonable_encoder(data1)
        
        answer = Answers_DB(
            answer_content=data1.get('answer_content'),
            answer_image=data1.get('answer_image'),
        )


        # insert to answers table
        id_answer = questions_db[QUESTIONS].insert_one(jsonable_encoder(answer)).inserted_id

        answer = jsonable_encoder(answer)
        answer.update({'answer_id': str(id_answer)})

        return JSONResponse(content={'status': 'success', 'data': answer},status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
