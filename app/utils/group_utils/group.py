from configs.settings import GROUP_PARTICIPANT, GROUP_QUESTIONS, group_db
from bson import ObjectId
from fastapi.responses import JSONResponse


def check_owner_or_user_of_group(user_id: str, group_id: str):
    # Find a group
    query = {'_id': ObjectId(group_id)}
    group = group_db.get_collection('group').find_one(query)
    if group:
        # check owner of group or member
        query_member = {
            'group_id': group_id,
            'user_id': user_id
        }
        member_group = group_db[GROUP_PARTICIPANT].find_one(query_member)
        if (group.get('owner_id') != user_id) and not member_group:
            content = {'status': 'Failed', 'msg': 'User is not the owner or member of group'}
            return False
        return True
    else:
        return False

def get_list_group_question(group_id: str):
    all_question = group_db[GROUP_QUESTIONS].find({'group_id': group_id}, {'question_id': 1})
    res = []
    for question in all_question:
        res.append(question.get('question_id'))
    return res