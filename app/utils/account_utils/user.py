from configs.logger import logger
from configs.settings import ADMIN_COLLECTION, user_db


def check_is_admin(user_id:str):
    try:
        admin_data = user_db[ADMIN_COLLECTION].find_one({
            'user_id': user_id
        })
        if admin_data:
            return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False