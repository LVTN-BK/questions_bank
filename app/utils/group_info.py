from bson import ObjectId
from configs import group_db


def get_one_group_info(group_id: str):
    query = {'_id': ObjectId(group_id)}
    group = group_db.get_collection('group').find_one(query)
    if group:
        group['_id'] = group_id
        return group
    else:
        return {}

def get_one_group_name_and_avatar(group_id: str):
    query = {'_id': ObjectId(group_id)}
    group = group_db.get_collection('group').find_one(query,{'group_name': 1, 'group_avatar': 1})
    if group:
        group['_id'] = group_id
        return group
    else:
        return {}