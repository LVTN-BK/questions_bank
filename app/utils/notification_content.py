from models.system_and_feeds.notification import NotificationContentManage, NotificationTypeManage


def get_notification_content(noti_type: str):
    content = ''
    if noti_type == NotificationTypeManage.COMMENT:
        content = NotificationContentManage.COMMENT
    elif noti_type == NotificationTypeManage.GROUP_SHARE_QUESTION:
        content = NotificationContentManage.GROUP_SHARE_QUESTION
    elif noti_type == NotificationTypeManage.COMMUNITY_SHARE_QUESTION:
        content = NotificationContentManage.COMMUNITY_SHARE_QUESTION
    elif noti_type == NotificationTypeManage.LOGGIN:
        content = NotificationContentManage.LOGGIN
    return content