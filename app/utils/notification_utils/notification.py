from datetime import datetime
from app.utils.notification_utils.check_noti_setting import get_list_user_id_enable_noti_type
from app.utils.group_utils.group import get_group_members_id_except_user
from app.utils.notification_utils.notification_content import get_notification_content
from configs.logger import logger
from models.db.notification import Notification_DB
from models.request.notification import DATA_Create_Noti_Group_Members_Except_User, DATA_Create_Noti_List_User
from fastapi.encoders import jsonable_encoder
from configs.settings import NOTI_COLLECTION, noti_db
from app.api_views import notification_manage




async def create_notification_to_list_specific_user(
    data: DATA_Create_Noti_List_User
): 
    try:
        logger().info('===============send_notification_to_list_specific_user=================')
        # filter user_id enable notification with noti_type
        # get_list_user_id_enable_noti_type(list_users=data.list_users, noti_type=data.noti_type)

        #get notification content
        content = get_notification_content(noti_type=data.noti_type)
        
        # filter user enable with notification type
        get_list_user_id_enable_noti_type(list_users=data.list_users, noti_type=data.noti_type)
        
        if data.list_users:
            # insert to DB
            new_noti = Notification_DB(
                sender_id=data.sender_id,
                receiver_ids=data.list_users,
                noti_type=data.noti_type,
                content=content,
                target=jsonable_encoder(data.target),
                seen_ids=[],
                removed_ids=[],
                datetime_created=datetime.now().timestamp()
            )
            json_data = jsonable_encoder(new_noti)
            _id = noti_db['notification'].insert_one(json_data).inserted_id

            json_data['_id'] = str(json_data['_id'])
            del json_data['receiver_ids']
            del json_data['seen_ids']
            del json_data['removed_ids']

            # Broastcast to active user:
            await notification_manage.broadcast_notification_to_list_specific_user(receive_ids=data.list_users, json_data=json_data, noti_type=data.noti_type)

        return True
    except Exception as e:
        logger().error(e)
        return False

async def create_notification_to_group_members_except_user(
    data: DATA_Create_Noti_Group_Members_Except_User
):
    try:
        # get receiver ids
        receive_ids = get_group_members_id_except_user(group_id=data.group_id, user_id=data.sender_id)
        
        #get notification content
        content = get_notification_content(noti_type=data.noti_type)

        # filter user enable with notification type
        get_list_user_id_enable_noti_type(list_users=receive_ids, noti_type=data.noti_type)

        if receive_ids:
            # insert to DB
            new_noti = Notification_DB(
                sender_id=data.sender_id,
                receiver_ids=receive_ids,
                noti_type=data.noti_type,
                content=content,
                target=jsonable_encoder(data.target),
                datetime_created=datetime.now().timestamp()
            )
            json_data = jsonable_encoder(new_noti)
            _id = noti_db[NOTI_COLLECTION].insert_one(json_data).inserted_id

            json_data['_id'] = str(json_data['_id'])
            del json_data['receiver_ids']
            del json_data['seen_ids']
            del json_data['removed_ids']

            # Broastcast to active members:
            await notification_manage.broadcast_notification_to_list_specific_user(receive_ids=receive_ids, json_data=json_data)

        return True
    except Exception as e:
        logger().error(e)
        return False

