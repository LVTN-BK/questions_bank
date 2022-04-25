from models.system_and_feeds.notification import NotificationContentManage, NotificationTypeManage


def get_notification_content(noti_type: str):
    content = ''
    if noti_type == NotificationTypeManage.COMMENT:
        content = NotificationContentManage.COMMENT
    elif noti_type == NotificationTypeManage.SHARE:
        content = NotificationContentManage.SHARE
    elif noti_type == NotificationTypeManage.LOGGIN:
        content = NotificationContentManage.LOGGIN
    return content