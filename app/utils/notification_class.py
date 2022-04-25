from typing import Dict, List, Union
from bson import ObjectId
from app.utils.check_noti_setting import get_list_user_id_enable_noti_type
from configs import GROUP_PROVIDER_API
from fastapi import WebSocket

import requests
from configs import LIST_PROVIDER_API
from fastapi import status

from configs.logger import logger          
    
class NotificationsManage:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def get_group_members_id(self, group_id):
        try:
            check_data = {
                'group_id': group_id,
            }
            logger().info(f'check_data: {check_data}')
            response = requests.post(GROUP_PROVIDER_API[0], data=check_data)
            logger().info(response)
            if response.status_code != status.HTTP_200_OK:
                return []
            else:
                return response.json().get('data')
        except Exception as e:
            logger().info(e)
            return []
    
    async def get_group_members_id_except_user(self, group_id: str, user_id: str, noti_type: str=None):
        try:
            #get list group members
            check_data = {
                'group_id': group_id,
            }
            response = requests.get(GROUP_PROVIDER_API['list_group_members'], 
                params=check_data
            )
            logger().info(response.status_code)
            logger().info(response.json())
            if response.status_code == 200:
                members = response.json().get('data').get('members')
                members.remove(user_id)
                logger().info(f'members: {members}')
                if noti_type:
                    #filter user_id enable notification with noti_type
                    get_list_user_id_enable_noti_type(list_users=members, noti_type=noti_type)
                logger().info(f'members after filter: {members}')
                return members
            else:
                return []
        except Exception as e:
            logger().error(e)
            return []
    
    async def get_active_group_members_websocket(self, group_id) -> List[WebSocket]:
        try:
            all_group_members = await self.get_group_members_id(group_id)
            active_members = []
            for uid in all_group_members:
                if uid in self.connections.keys():
                # if self.connections[uid]:
                    # active_members.append(self.connections[uid])
                    active_members.extend(self.connections[uid])
            return active_members
        except Exception as e:
            logger().error(e)
            return []
    
    async def get_active_list_specific_user_websocket(self, list_user_id) -> List[WebSocket]:
        try:
            active_members = []
            for uid in list_user_id:
                if uid in self.connections.keys():
                # if self.connections[uid]:
                    # active_members.append(self.connections[uid])
                    active_members.extend(self.connections[uid])
            logger().info(f'active members: {active_members}')
            return active_members
        except Exception as e:
            logger().error(e)
            return []
    
    async def get_active_group_members_websocket_except_user(self, group_id, user_id, noti_type: str=None) -> List[WebSocket]:
        try:
            all_group_members = await self.get_group_members_id_except_user(group_id=group_id, user_id=user_id, noti_type=noti_type)
            active_members = []
            for uid in all_group_members:
                if uid in self.connections.keys():
                # if self.connections[uid]:
                    # active_members.append(self.connections[uid])
                    active_members.extend(self.connections[uid])
            return active_members
        except Exception as e:
            logger().error(e)
            return []

    def remove_active_member(self, user_id: str, websocket: WebSocket):
        self.connections[user_id].remove(websocket)
        if not self.connections[user_id]:
            del self.connections[user_id]
    
    async def broadcast_notification_to_group_active_members(self, group_id, json_data):
        try:
            active_members = await self.get_active_group_members_websocket(group_id)
            logger().info(f'active_member: {active_members}')
            for connection in active_members:
                try:
                    await connection.send_json(json_data)
                except Exception:
                    pass
        except Exception as e:
            logger().info(f'Error occurs {e.args}')
    
    async def broadcast_notification_to_group_active_members_except_user(self, group_id, user_id, json_data, noti_type: str=None):
        try:
            active_members = await self.get_active_group_members_websocket_except_user(group_id=group_id, user_id=user_id, noti_type=noti_type)
            logger().info(f'active_member: {active_members}')
            for connection in active_members:
                try:
                    await connection.send_json(json_data)
                except Exception:
                    pass
        except Exception as e:
            logger().info(f'Error occurs {e.args}')
    
    async def broadcast_notification_to_list_specific_user(self, receive_ids, json_data):
        try:
            active_members = await self.get_active_list_specific_user_websocket(receive_ids)
            logger().info(f'active_member: {active_members}')
            for connection in active_members:
                try:
                    await connection.send_json(json_data)
                except Exception:
                    pass
        except Exception as e:
            logger().info(f'Error occurs {e.args}')

    async def broadcast_message_to_all_active_members(self, json_data):
        try:
            logger().info(self.connections.items())
            for uid, conn in self.connections.items():
                logger().info(f'uid: {uid}')
                logger().info(f'conn: {conn}')
                for con in conn:
                    await con.send_json(json_data)
        except Exception as e:
            logger().info(f'Error occurs {e}')

    async def connect(self, websocket:WebSocket,user_id, token: str):
        logger().info('################################################')
        await websocket.accept()
        check_data = {
            'user_id': user_id,
            'token': token
        }
        # response = requests.post(LIST_PROVIDER_API[1], check_data)
        # if response.status_code != status.HTTP_200_OK:
        #     await websocket.send_json(response.json())
        #     await websocket.close()
        #     return False
        
        #add connection to group connections list
        if user_id not in self.connections.keys():
            self.connections[user_id] = [websocket]
        else:
            self.connections[user_id].append(websocket)

        # Save or update current user with respective token to auth_token document
        # await save_user_token(user_id, token)
        return True
        