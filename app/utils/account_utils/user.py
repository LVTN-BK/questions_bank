from configs.logger import logger
from configs.settings import ADMIN_COLLECTION, USERS_PROFILE, user_db


def check_is_admin(user_id:str):
    try:
        logger().info('==============check is admin===============')
        admin_data = user_db[ADMIN_COLLECTION].find_one({
            'user_id': user_id
        })
        logger().info(admin_data)
        if admin_data:
            return True
        else:
            return False
    except Exception as e:
        logger().error(e)
        return False


def get_user_info(user_id: str):
    try:
        pipeline = [
            {
                '$match': {
                    'user_id': user_id
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': 1,
                    'name': {
                        '$ifNull': ['$name', None]
                    },
                    'email': {
                        '$ifNull': ['$email', None]
                    },
                    'avatar': {
                        '$ifNull': ['$avatar', None]
                    }
                }
            }
        ]
        user_data = user_db[USERS_PROFILE].aggregate(pipeline)
        if user_data.alive:
            result = user_data.next()
            return result
        else:
            return {}
    except Exception:
        return {}
