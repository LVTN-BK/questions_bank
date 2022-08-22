from app.utils.notification_utils.notification import create_notification_to_list_specific_user, create_notification_to_group_members_except_user
from configs.settings import COMMENTS, EXAMS, GROUP_JOIN_REQUEST, QUESTIONS, group_db, questions_db, comments_db
from models.define.target import ManageTargetType
from models.request.comment import DATA_Create_Comment, DATA_Create_Reply_Comment
from models.request.group import DATA_Accept_Join_Request, DATA_Invite_Members, DATA_Reject_Join_Request
from models.request.like import DATA_Create_Like
from models.request.notification import DATA_Create_Noti_Group_Members_Except_User, DATA_Create_Noti_List_User, TargetData
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

        data_noti_group = DATA_Create_Noti_Group_Members_Except_User(
            sender_id=user_id,
            group_id=data.group_id,
            noti_type=NotificationTypeManage.GROUP_SHARE_QUESTION,
            target=target_data
        )
        create_notification_to_group_members_except_user(data_noti_group)

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

    def group_invite_member(
        data: DATA_Invite_Members,
        user_id: str
    ):        
        target_data = TargetData(
            group_id=data.group_id,
        )

        data_noti = DATA_Create_Noti_List_User(
            sender_id=user_id,
            list_users=data.list_user_ids,
            noti_type=NotificationTypeManage.GROUP_INVITE_MEMBER,
            target=target_data
        )
        create_notification_to_list_specific_user(data_noti)

    def create_comment(
        data: DATA_Create_Comment,
        user_id: str
    ):        
        if data.target_type == ManageTargetType.QUESTION:
            # find question
            question_info = questions_db[QUESTIONS].find_one(
                {
                    '_id': ObjectId(data.target_id)
                }
            )
            if question_info and (question_info.get('user_id') != user_id):
                target_data = TargetData(
                    question_id=data.target_id,
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[question_info.get('user_id')],
                    noti_type=NotificationTypeManage.COMMENT_QUESTION,
                    target=target_data
                )
            else:
                return
        else:
            # find exam
            exam_info = questions_db[EXAMS].find_one(
                {
                    '_id': ObjectId(data.target_id)
                }
            )
            if exam_info and (exam_info.get('user_id') != user_id):
                target_data = TargetData(
                    exam_id=data.target_id,
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[exam_info.get('user_id')],
                    noti_type=NotificationTypeManage.COMMENT_EXAM,
                    target=target_data
                )
            else:
                return

        create_notification_to_list_specific_user(data_noti)

    def create_reply_comment(
        data: DATA_Create_Reply_Comment,
        user_id: str
    ):   
        # find comment
        comment_data = comments_db[COMMENTS].find_one(
            {
                '_id': ObjectId(data.comment_id),
                'is_removed': False
            }
        )
        if comment_data and (comment_data.get('user_id') != user_id):  
            if comment_data.get('target_type') == ManageTargetType.QUESTION:
                target_data = TargetData(
                    question_id=comment_data.get('target_id'),
                    comment_id=data.comment_id
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[comment_data.get('user_id')],
                    noti_type=NotificationTypeManage.REPLY_COMMENT,
                    target=target_data
                )
            elif comment_data.get('target_type') == ManageTargetType.EXAM:
                target_data = TargetData(
                    exam_id=comment_data.get('target_id'),
                    comment_id=data.comment_id
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[comment_data.get('user_id')],
                    noti_type=NotificationTypeManage.REPLY_COMMENT,
                    target=target_data
                )
            else:
                return
        else:
            return

        create_notification_to_list_specific_user(data_noti)

    def create_like(
        data: DATA_Create_Like,
        user_id: str
    ):        
        if data.target_type == ManageTargetType.QUESTION:
            # find question
            question_info = questions_db[QUESTIONS].find_one(
                {
                    '_id': ObjectId(data.target_id)
                }
            )
            if question_info and (question_info.get('user_id') != user_id):
                target_data = TargetData(
                    question_id=data.target_id,
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[question_info.get('user_id')],
                    noti_type=NotificationTypeManage.LIKE_QUESTION,
                    target=target_data
                )
            else:
                return
        else:
            # find exam
            exam_info = questions_db[EXAMS].find_one(
                {
                    '_id': ObjectId(data.target_id)
                }
            )
            if exam_info and (exam_info.get('user_id') != user_id):
                target_data = TargetData(
                    exam_id=data.target_id,
                )

                data_noti = DATA_Create_Noti_List_User(
                    sender_id=user_id,
                    list_users=[exam_info.get('user_id')],
                    noti_type=NotificationTypeManage.LIKE_EXAM,
                    target=target_data
                )
            else:
                return

        create_notification_to_list_specific_user(data_noti)

