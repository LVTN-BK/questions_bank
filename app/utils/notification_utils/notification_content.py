from models.define.notification import NotificationContentManage, NotificationTypeManage


def get_notification_content(noti_type: str):
    content = ''
    if noti_type == NotificationTypeManage.COMMENT_QUESTION:
        content = NotificationContentManage.COMMENT_QUESTION
    elif noti_type == NotificationTypeManage.COMMENT_EXAM:
        content = NotificationContentManage.COMMENT_EXAM
    elif noti_type == NotificationTypeManage.REPLY_COMMENT:
        content = NotificationContentManage.REPLY_COMMENT
    elif noti_type == NotificationTypeManage.LIKE_QUESTION:
        content = NotificationContentManage.LIKE_QUESTION
    elif noti_type == NotificationTypeManage.LIKE_EXAM:
        content = NotificationContentManage.LIKE_EXAM
    elif noti_type == NotificationTypeManage.GROUP_SHARE_QUESTION:
        content = NotificationContentManage.GROUP_SHARE_QUESTION
    elif noti_type == NotificationTypeManage.GROUP_SHARE_EXAM:
        content = NotificationContentManage.GROUP_SHARE_EXAM
    elif noti_type == NotificationTypeManage.GROUP_INVITE_MEMBER:
        content = NotificationContentManage.GROUP_INVITE_MEMBER
    elif noti_type == NotificationTypeManage.GROUP_ACCEPT_REQUEST:
        content = NotificationContentManage.GROUP_ACCEPT_REQUEST
    elif noti_type == NotificationTypeManage.GROUP_REJECT_REQUEST:
        content = NotificationContentManage.GROUP_REJECT_REQUEST
    elif noti_type == NotificationTypeManage.USER_REQUEST_JOIN_GROUP:
        content = NotificationContentManage.USER_REQUEST_JOIN_GROUP
    return content