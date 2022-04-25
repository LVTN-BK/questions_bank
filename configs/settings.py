import os
import time, threading
from pathlib import Path
import urllib.parse
import pymongo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pymongo import MongoClient

from configs.tags_metadata import TAGS_METADATA
from configs.logger import *

DEBUG = int(os.environ.get('DEBUG', 1))

# Initial FastAPI app
app = FastAPI(
    debug=bool(DEBUG),
    title='Questions Bank API'
)


# def custom_openapi():
#     openapi_schema = get_openapi(
#         title='questions bank',
#         description='pattern',
#         version='1.0',
#         tags=TAGS_METADATA,
#         routes=app.routes
#     )
#     openapi_schema['info']['x-logo'] = {
#         'url': '#'
#     }
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema


# app.openapi = custom_openapi

# Provide which origins should be accepted to call apis
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# RABBITMQ = os.environ.get('RABBITMQ')
# DB_HOST = os.environ.get('DB_HOST')
# DB_PORT = os.environ.get('DB_PORT')

MONGO_DEFAULT_USER = os.environ.get('MONGO_DEFAULT_USER')
MONGO_DEFAULT_PASS = os.environ.get('MONGO_DEFAULT_PASS')

# MONGO_CLIENT = MongoClient(f'mongodb://{MONGO_DEFAULT_USER}:{MONGO_DEFAULT_PASS}@<DB_HOST>:<DB_PORT>/authSource?authSource=admin&authMechanism=SCRAM-SHA-256')
MONGO_CLIENT = MongoClient(f'mongodb+srv://root:root@cluster0.3n45m.mongodb.net/question-bank?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')
SYSTEM = MONGO_CLIENT['question-bank']

##############################################
# notification db
noti_db = MONGO_CLIENT['notification-db']
NOTI_COLLECTION = 'notification'
NOTI_SETTING_COLLECTION = 'notification_setting'

#create index for notification
noti_db[NOTI_COLLECTION].create_index([('datetime_created', pymongo.DESCENDING)])

# create combound index:
noti_db[NOTI_SETTING_COLLECTION].create_index([('user_id', pymongo.ASCENDING), ('noti_type', pymongo.ASCENDING)])


#############################################
# group db
group_db = MONGO_CLIENT['group-db']
GROUP = 'group'
GROUP_LABEL = 'group_label'
GROUP_INVITATION = 'group_invitation'
GROUP_PARTICIPANT = 'group_participant'
GROUP_JOIN_REQUEST = 'group_join_request'
group_db[GROUP_INVITATION].create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)
group_db[GROUP_JOIN_REQUEST].create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)

#create text index for group name
group_db.get_collection(GROUP).create_index([('group_name', 'text')])


#create index for group_participant
group_db.get_collection('group_participant').create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)


LIST_PROVIDER_API = [
]

FEED_PROVIDER_API = [
]

GROUP_PROVIDER_API = {
}
