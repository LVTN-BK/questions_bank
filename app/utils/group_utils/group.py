from datetime import datetime
from configs.logger import logger
from configs.settings import GROUP, GROUP_EXAMS, GROUP_PARTICIPANT, GROUP_QUESTIONS, group_db
from bson import ObjectId
from fastapi.responses import JSONResponse
from models.db.group import GroupMember
from fastapi.encoders import jsonable_encoder

from models.define.group import GroupStatus


def check_group_exist(group_id: str):
    query = {
        '_id': ObjectId(group_id),
        'is_deleted': False,
        'group_status': GroupStatus.ENABLE
    }
    group = group_db[GROUP].find_one(query)
    if group:
        return group
    else:
        return False

def check_owner_or_user_of_group(user_id: str, group_id: str):
    # check owner of group or member
    query_member = {
        'group_id': group_id,
        'user_id': user_id
    }
    member_group = group_db[GROUP_PARTICIPANT].find_one(query_member)
    if not member_group:
        return False
    return True

def check_owner_of_group(user_id: str, group_id: str):
    # check owner of group or member
    query_member = {
        'group_id': group_id,
        'user_id': user_id,
        'is_owner': True
    }
    member_group = group_db[GROUP_PARTICIPANT].find_one(query_member)
    if not member_group:
        return False
    return True

def get_list_group_question(group_id: str):
    all_question = group_db[GROUP_QUESTIONS].find({'group_id': group_id}, {'question_id': 1})
    res = []
    for question in all_question:
        res.append(question.get('question_id'))
    return res

def get_list_group_exam(group_id: str):
    all_exam = group_db[GROUP_EXAMS].find({'group_id': group_id}, {'exam_id': 1})
    res = []
    for exam in all_exam:
        res.append(exam.get('exam_id'))
    return res

def insert_group_participant(user_id: str, group_id: str, is_owner: bool = False, inviter_id: str = None):
    try:
        data = GroupMember(
            user_id = user_id, 
            group_id = group_id, 
            is_owner=is_owner,
            inviter_id = inviter_id, 
            datetime_created = datetime.now().timestamp()
        )
        insert = group_db[GROUP_PARTICIPANT].insert_one(jsonable_encoder(data))
           
    except (Exception, ) as e:
        logger().info("Error: ", e.__str__())
        raise Exception(str(e))

def get_list_group_member_id(group_id: str):
    all_group_member = group_db[GROUP_PARTICIPANT].find({'group_id': group_id}, {'user_id': 1})
    res = []
    for question in all_group_member:
        res.append(question.get('user_id'))
    return res

def get_group_members_id_except_user(group_id: str, user_id: str):
    try:
        #get list group members
        all_group_member = group_db[GROUP_PARTICIPANT].find({'group_id': group_id}, {'user_id': 1})
        res = []
        for question in all_group_member:
            res.append(question.get('user_id'))
        res.remove(user_id)
        logger().info(f'members: {res}')
        return res
    except Exception as e:
        logger().error(e)
        return []




