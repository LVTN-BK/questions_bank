from functools import wraps
from fastapi import status
from fastapi.responses import JSONResponse
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