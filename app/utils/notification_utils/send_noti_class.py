from app.utils.notification_utils.notification import create_notification_to_list_specific_user
from configs.settings import GROUP_JOIN_REQUEST, group_db
from models.request.group import DATA_Accept_Join_Request, DATA_Reject_Join_Request
from models.request.notification import DATA_Create_Noti_List_User, TargetData
from models.request.question import DATA_Share_Question_To_Group
from models.system_and_feeds.notification import NotificationTypeManage
from fastapi import BackgroundTasks
from bson import ObjectId


class SendNotification:
    def group_share_question(
        data: DATA_Share_Question_To_Group,
        user_id: str
    ):
        target_data = TargetData(
            group_id=data.group_id,
            question_id=data.question_id
        )

        data_noti = DATA_Create_Noti_List_User(
            sender_id=user_id,
            list_users=[user_id],
            noti_type=NotificationTypeManage.GROUP_SHARE_QUESTION,
            target=target_data
        )
        create_notification_to_list_specific_user(data_noti)
    def group_accept_request_join(
        data: DATA_Accept_Join_Request,
        user_id: str
    ):
        #find request join
        query_request = {
            '_id': ObjectId(data.request_id)
        }
        #remove request join
        data_request = group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)
        if data_request:
            target_data = TargetData(
                group_id=data_request.get('group_id'),
            )

            data_noti = DATA_Create_Noti_List_User(
                sender_id=user_id,
                list_users=[data_request.get('user_id')],
                noti_type=NotificationTypeManage.GROUP_ACCEPT_REQUEST,
                target=target_data
            )
            create_notification_to_list_specific_user(data_noti)
    def group_reject_request_join(
        data: DATA_Reject_Join_Request,
        user_id: str
    ):
        #find request join
        query_request = {
            '_id': ObjectId(data.request_id)
        }
        #remove request join
        data_request = group_db[GROUP_JOIN_REQUEST].find_one_and_delete(query_request)
        if data_request:
            target_data = TargetData(
                group_id=data_request.get('group_id'),
            )

            data_noti = DATA_Create_Noti_List_User(
                sender_id=user_id,
                list_users=[data_request.get('user_id')],
                noti_type=NotificationTypeManage.GROUP_REJECT_REQUEST,
                target=target_data
            )
            create_notification_to_list_specific_user(data_noti)