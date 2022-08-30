from functools import wraps
from app.utils.notification_utils.send_noti_class import SendNotification

from configs.logger import logger
class SendNotiDecoratorsApi:
    def group_share_question(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.group_share_question,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner
    
    def group_share_exam(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.group_share_exam,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def group_accept_request_join(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.group_accept_request_join,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner
        
    def group_reject_request_join(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.group_reject_request_join,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def group_invite_member(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.group_invite_member,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def user_request_join_group(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.user_request_join_group,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def create_comment(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.create_comment,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def create_reply_comment(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.create_reply_comment,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

    def create_like(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            response_data = await func(*args, **kwargs)
            if response_data.status_code == 200:
                kwargs.get("background_tasks").add_task(
                    SendNotification.create_like,
                    data=kwargs.get("data"), 
                    user_id=kwargs.get("data2").get('user_id')
                )
            return response_data
        return inner

