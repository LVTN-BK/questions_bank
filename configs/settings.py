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

from dotenv import load_dotenv

load_dotenv()

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
SECRET_KEY = os.environ.get('SECRET_KEY')
MAIL_API_KEY = os.environ.get('MAIL_API_KEY')

MONGO_DEFAULT_USER = os.getenv('MONGO_DEFAULT_USER')
MONGO_DEFAULT_PASS = os.getenv('MONGO_DEFAULT_PASS')

# MONGO_CLIENT = MongoClient(f'mongodb://{MONGO_DEFAULT_USER}:{MONGO_DEFAULT_PASS}@<DB_HOST>:<DB_PORT>/authSource?authSource=admin&authMechanism=SCRAM-SHA-256')
MONGO_CLIENT = MongoClient(f'mongodb+srv://root:root@cluster0.3n45m.mongodb.net/question-bank?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')

################################################
# user
SYSTEM = MONGO_CLIENT['user-db']
user_db = MONGO_CLIENT['user-db']
USER_COLLECTION = 'users'
USERS_PROFILE = 'users_profile'

##############################################
# notification db
noti_db = MONGO_CLIENT['questions-db']
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
GROUP_QUESTIONS = 'group_questions'
GROUP_EXAMS = 'group_exams'
group_db[GROUP_INVITATION].create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)
group_db[GROUP_JOIN_REQUEST].create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)

#create text index for group name
group_db.get_collection(GROUP).create_index([('group_name', 'text')])

#create index for group_participant
group_db.get_collection('group_participant').create_index([('group_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)


############################################
#question db
questions_db = MONGO_CLIENT['questions-db']
QUESTIONS = 'questions'
QUESTIONS_VERSION = 'questions_version'
ANSWERS = 'answers'
#create text index for group name
questions_db[QUESTIONS_VERSION].create_index([('question_content', 'text')])


############################################
#exam db
exams_db = MONGO_CLIENT['questions-db']
EXAMS = 'exams'
EXAMS_VERSION = 'exams_version'
#create text index for group name
questions_db[EXAMS_VERSION].create_index([('exam_title', 'text')])

############################################
#like db
likes_db = MONGO_CLIENT['likes-db']
LIKES = 'likes'
#create index for like db
likes_db[LIKES].create_index([('user_id', pymongo.ASCENDING), ('target_id', pymongo.ASCENDING)], unique=True)


############################################
#comment db
comments_db = MONGO_CLIENT['comments-db']
COMMENTS = 'comments'
REPLY_COMMENTS = 'reply_comments'


############################################
#classify db
classify_db = MONGO_CLIENT['questions-db']
SUBJECT = 'subject'
CLASS = 'class'
CHAPTER = 'chapter'
TAG_COLLECTION = 'tag'
