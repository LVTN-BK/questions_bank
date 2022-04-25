from configs import NOTI_SETTING_COLLECTION
from configs import noti_db


def get_list_user_id_enable_noti_type(list_users: str, noti_type: str):
    for user_id in list_users:
        query = {
            'user_id': user_id,
            'noti_type': noti_type,
            'is_enable': False
        }
        noti_disable = noti_db[NOTI_SETTING_COLLECTION].find_one(query)
        if noti_disable:
            list_users.remove(user_id)