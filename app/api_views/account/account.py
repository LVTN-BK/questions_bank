from fastapi import status, Form
from fastapi import Body, Depends, Query
from app.utils.account_utils.account import send_reset_password_email, send_verify_email, send_verify_update_email
from models.db.account import User
from models.define.user import UserInfo
from models.request.account import DATA_Accept_Update_Email, DATA_Apply_Reset_Password, DATA_Reset_Password, DATA_Update_Account, DATA_Update_Password, DATA_Verify_Update_Email
from pymongo.collection import ReturnDocument
from starlette.responses import JSONResponse
from configs.settings import SYSTEM, USER_COLLECTION, USERS_PROFILE, app, user_db
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

# from cryptography.fernet import Fernet

from models.response.account import CreateAccountResponse200, CreateAccountResponse403, GetAccount200, GetAccount403, LoginResponse200, LoginResponse403, PutResetPasswordResponse200, PutResetPasswordResponse400, ResetPasswordResponse201, ResetPasswordResponse404, Token

from configs.logger import *

#===========================================
#==============LOGIN========================
#===========================================
@app.post(
    path='/login',
    responses={
        status.HTTP_200_OK: {
            'model': LoginResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': LoginResponse403
        }
    },
    tags=['system_account']
)
async def login_system(
    email: EmailStr = Body(...), 
    password: str = Body(...)
):
    try:
        user = SYSTEM['users'].find_one(
            {
                'email': {
                    '$eq': email
                },
                'is_verified': True,
                'is_disable': False
            }
        )
        if user is None:
            msg = 'Tài khoản không tồn tại hoặc chưa xác thực!'
            return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        
        if verify_password(password, user.get('hashed_password')):
            # Create new access token for user
            # secret_key = user.get('secret_key')
            access_token= create_access_token(
                data={
                    'email': user.get('email'),
                    'user_id': str(user.get('_id'))
                }
                # secret_key=secret_key
            )
            user = SYSTEM['users'].find_one_and_update(
                {'email': {'$eq': email}},
                {
                    '$set': {
                        'token.access_token': access_token
                    }
                },
                return_document=ReturnDocument.AFTER
            )

            pipeline = [
                {
                    '$match': {
                        'user_id': str(user.get('_id'))
                    }
                },
                {
                    '$lookup': {
                        'from': 'admin',
                        'pipeline': [
                            {
                                '$match': {
                                    'user_id': str(user.get('_id'))
                                }
                            }
                        ],
                        'as': 'admin_data'
                    }
                },
                {
                    '$set': {
                        'is_admin': {
                            '$ne': ['$admin_data', []]
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'admin_data': 0
                    }
                }
            ]
            user_info = SYSTEM[USERS_PROFILE].aggregate(pipeline)
            if user_info.alive:
                user_info = user_info.next()
            else:
                raise Exception('user not found!')

            # user_info_return = UserInfo(id=str(user.get('_id')), avatar=user_info.get('avatar'))
            return JSONResponse(content={'token': user.get('token'), 'user': user_info},
                                status_code=status.HTTP_200_OK)
        else:
            msg = 'Tài khoản hoặc mật khẩu không đúng!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#==============CREATE_SYSTEM_ACCOUNT========
#===========================================
@app.post(
    path='/account',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, tags=['system_account']
)
async def create_system_account(
        email: EmailStr = Body(..., description='Email'),
        name: str = Body(..., description='name'),
        password: str = Body(..., description='Password'),
):
    try:
        # Check if user already exist
        if SYSTEM['users'].find({"email": {"$eq": email}}).count():
            return JSONResponse(content={
                "status": "Failed",
                "msg": "Email is existing for another account"
            }, status_code=status.HTTP_403_FORBIDDEN)
        

        # #Thêm encrypt password
        # key = Fernet.generate_key()
        # fernet = Fernet(key)

        import secrets
        keyonce = secrets.token_urlsafe(12)
        await send_verify_email(to_email=email, keyonce=keyonce)

        user = User(
            name=name,
            # token=token,
            # secret_key=secret_key,
            email=email,
            hashed_password=get_password_hash(password),
            # encrypt_password=fernet.encrypt(password.encode()), #pass
            # encrypt_key=key,  
            key_verify=keyonce,                                   #key
            datetime_created=datetime.now()
        )

        # Create user in db
        user_id = SYSTEM[USER_COLLECTION].insert_one(
            jsonable_encoder(user)
        ).inserted_id

        # insert to user profile
        query_profile = {
            'user_id': str(user_id),
            'name': name,
            'email': email
        }
        SYSTEM[USERS_PROFILE].insert_one(
            query_profile
        )

        # Update access token, secret key
        access_token = create_access_token(
            data={
                'email': email,
                'user_id': str(user_id)
            }
        )

        token = Token(
            access_token=access_token,
            token_type='Bearer'
        )
        
        user = SYSTEM['users'].find_one(
            {'email': {'$eq': email}},
        )

        query_update = {
            '$set': {
                'token': jsonable_encoder(token)
            }      
        }

        SYSTEM['users'].update_one(
            {'email': {'$eq': email}},
            query_update
        )

        return JSONResponse(content={
            'status': 'Created',
        }, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)


# #===========================================
# #==============GET_ACCOUNT_INFO=============
# #===========================================
# @app.post(
#     path= '/get_account_info',
#     responses={
#         status.HTTP_200_OK: {
#             'model': GetAccount200
#         },
#         status.HTTP_403_FORBIDDEN: {
#             'model': GetAccount403
#         }
#     },
#     tags=['system_account']
# )
# async def get_account_info(email: EmailStr = Form(...)):
#     user = SYSTEM['users'].find_one({'email': {'$eq': email}})
#     if user is None:
#         return JSONResponse(content={'status': 'Email not exist'}, status_code=status.HTTP_403_FORBIDDEN)
#     else:
#         try:
#             email = user.get('email')

#             key = user.get('encrypt_key')
#             fernet = Fernet(key)

#             encrypt_password = bytes(user.get('encrypt_password'), 'utf-8')
#             password=fernet.decrypt(encrypt_password).decode()

#             return JSONResponse(content={'email': email, 'password': password}, status_code=status.HTTP_200_OK)
#         except Exception as e:
#             logger().error(e)
#             return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)


#===========================================
#===============UPDATE_ACCOUNT_INFO=========
#===========================================
@app.put(
    path='/update_account_info',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, 
    tags=['system_account']
)
async def update_account_info(
    data1: DATA_Update_Account,
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_account_info======================')
    try:
        field_update = {}
        data1 = jsonable_encoder(data1)
        for key in data1.keys():
            if data1.get(key):
                field_update.update({key: data1.get(key)})
        logger().info(field_update)
        query_update = {
            '$set': field_update
        }
        SYSTEM[USERS_PROFILE].update_one(
            {'user_id': {'$eq': data2.get('user_id')}},
            query_update
        )

        return JSONResponse(content={
            'status': 'success'
        }, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#=================UPDATE_AVATAR=============
#===========================================
@app.put(
    path='/update_avatar',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, 
    tags=['system_account']
)
async def update_avatar(
    avatar: str = Body(..., description='new avatar url'),
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_avatar======================')
    try:
        field_update = {
            'avatar': avatar
        }
        logger().info(field_update)
        query_update = {
            '$set': field_update
        }
        SYSTEM[USERS_PROFILE].update_one(
            {'user_id': {'$eq': data2.get('user_id')}},
            query_update
        )

        return JSONResponse(content={
            'status': 'success'
        }, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#=============VERIFY_UPDATE_EMAIL===========
#===========================================
@app.post(
    path='/verify_update_email',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, 
    tags=['system_account']
)
async def verify_update_email(
    data1: DATA_Verify_Update_Email,
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_email======================')
        
    try:
        new_email_usage = user_db[USER_COLLECTION].find_one({'email': {'$eq': data1.new_email}})
        data1 = jsonable_encoder(data1)
        if new_email_usage:
            msg = 'email exist in system!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        user = SYSTEM['users'].find_one({'email': {'$eq': data2.get('email')}})

        if verify_password(data1.get('password'), user.get('hashed_password')):
            # store key update email to db
            import secrets
            keyonce = secrets.token_urlsafe(6)
            expire_in = datetime.now() + timedelta(minutes=30)
            expire_at_timestamp = expire_in.timestamp()
            data_update_email = {
                'keyonce': keyonce,
                'keyonce_expire_at': expire_at_timestamp,
                'new_email': data1.get('new_email')
            }
            user_db[USER_COLLECTION].find_one_and_update(
                {
                    '_id': user.get('_id')
                },
                {
                    '$set': {
                        'data_update_email': data_update_email
                    }
                }
            )

            # send key to new email
            await send_verify_update_email(to_email=data1.get('new_email'), keyonce=keyonce)

            return JSONResponse(
                content={
                    'status': 'success'
                },
                status_code=status.HTTP_200_OK
            )
        else:
            msg = 'Sai mật khẩu!'
            return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#=============ACCEPT_UPDATE_EMAIL===========
#===========================================
@app.put(
    path='/accept_update_email',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, 
    tags=['system_account']
)
async def accept_update_email(
    data1: DATA_Accept_Update_Email,
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_email======================')
        
    try:
        user = SYSTEM['users'].find_one({'email': {'$eq': data2.get('email')}})

        data_update_email = user.get('data_update_email')
        if not data_update_email:
            msg = 'user not request update email yet!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        new_email_usage = user_db[USER_COLLECTION].find_one({'email': {'$eq': data_update_email.get('new_email')}})
        if new_email_usage:
            msg = 'email exist in system!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

        if data_update_email.get('keyonce_expire_at') < datetime.now().timestamp():
            msg = 'key update email is expired!'
            return JSONResponse(content={'status': 'failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
        elif data1.key_update_email == data_update_email.get('keyonce'):
            # Create new access token for user
            # secret_key = user.get('secret_key')
            access_token= create_access_token(
                data={
                    'email': data_update_email.get('new_email'),
                    'user_id': str(user.get('_id'))
                }
            )

            # update in user table
            user = SYSTEM['users'].find_one_and_update(
                {'_id': user.get('_id')},
                {
                    '$set': {
                        'email': data_update_email.get('new_email'),
                        'token.access_token': access_token,
                        # 'secret_key': secret_key
                    },
                    '$unset': {
                        'data_update_email': ''
                    }
                },
                return_document=ReturnDocument.AFTER
            )

            # update in user information table
            query_update = {
                '$set': {
                    'email': data_update_email.get('new_email')
                }
            }
            SYSTEM[USERS_PROFILE].find_one_and_update(
                {'user_id': str(user.get('_id'))},
                query_update
            )

            data = {
                'access_token': access_token, 
                # 'secret_key': secret_key,
                'email': data_update_email.get('new_email')
            }
            msg = 'update email successfully'
            return JSONResponse(
                content={
                    'status': 'success',
                    'data': data,
                    'msg': msg
                },
                status_code=status.HTTP_200_OK
            )
        else:
            msg = 'key is not correct'
            return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger().error(e)
        msg = 'Có lỗi xảy ra!'
        return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#================UPDATE_PASSWORD============
#===========================================
@app.put(
    path='/update_password',
    responses={
        status.HTTP_200_OK: {
            'model': CreateAccountResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': CreateAccountResponse403
        }
    }, 
    tags=['system_account']
)
async def update_password(
    data1: DATA_Update_Password,
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_password======================')
    data1 = jsonable_encoder(data1)
    user = SYSTEM['users'].find_one({'email': {'$eq': data2.get('email')}})
    if user is None:
        return JSONResponse(content={'status': 'Email not exist'}, status_code=status.HTTP_403_FORBIDDEN)
    try:
        if verify_password(data1.get('old_password'), user.get('hashed_password')):
            # update in user table
            user = SYSTEM['users'].find_one_and_update(
                {'email': {'$eq': data2.get('email')}},
                {
                    '$set': {
                        'hashed_password': get_password_hash(data1.get('new_password'))
                    }
                },
                return_document=ReturnDocument.AFTER
            )

            msg = 'update password successfully'
            return JSONResponse(
                content={
                    'status': 'success',
                    'msg': msg
                },
                status_code=status.HTTP_200_OK
            )
    except:
        logging.exception("Error occurred")
    msg = 'maybe password was wrong'
    return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#================RESET_PASSWORD=============
#===========================================
@app.post(
    path='/reset_password', 
    responses={
        status.HTTP_201_CREATED: {
            'model': ResetPasswordResponse201
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResetPasswordResponse404
        }
    }, 
    tags=['account']
)
async def reset_password(
    data: DATA_Reset_Password
):
    """ 
        Khôi phục lại mật khẩu, hệ thống gửi mail kèm theo mã để khôi phục lại mật khẩu
    """
    import secrets
    keyonce = secrets.token_urlsafe(6)
    expire_in = datetime.now() + timedelta(minutes=30)
    expire_at_timestamp = expire_in.timestamp()

    user = SYSTEM[USER_COLLECTION].find_one(
        filter={'email': {'$eq': data.email}}
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Email chưa đăng ký tài khoản!'}, status_code=status.HTTP_404_NOT_FOUND)
    
    # Check if keyonce is not used
    await send_reset_password_email(to_email=data.email, keyonce=keyonce)
    SYSTEM[USER_COLLECTION].find_one_and_update(
        filter={'email': {'$eq': data.email}},
        update={'$set': {
                'keyonce': keyonce,
                'keyonce_expire_at': expire_at_timestamp
            }
        }
    )
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Vui lòng kiểm tra email và nhập mã!'}, status_code=status.HTTP_201_CREATED)


#===========================================
#=============APPLY_RESET_PASSWORD==========
#===========================================
@app.put(
    path='/apply_reset_password', 
    responses={
        status.HTTP_200_OK: {
            'model': PutResetPasswordResponse200
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': PutResetPasswordResponse400
        }
    }, 
    tags=['account']
)
async def apply_reset_password(
    data: DATA_Apply_Reset_Password
):
    """Khôi phục lại mật khẩu"""
    if data.password != data.re_password:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mật khẩu không khớp!'}, status_code=status.HTTP_400_BAD_REQUEST)
    user = SYSTEM[USER_COLLECTION].find_one_and_update(
        filter={
            'keyonce': {'$eq': data.keyonce}, 'keyonce_expire_at': {'$gte': datetime.now().timestamp()}
        },
        update={
            '$set': {
                'tokens': [],
                'hashed_password': get_password_hash(data.password),
            },
            '$unset': {
                'keyonce': '',
                'keyonce_expire_at': ''
            }
        }
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mã hết thời gian hoặc không tồn tại!'}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Mật khẩu đã được thiết lập lại!'}, status_code=status.HTTP_200_OK)



#===========================================
#=================VERIFY_EMAIL==============
#===========================================
@app.get(
    path='/verify_email',
    responses={
        status.HTTP_200_OK: {
            'model': LoginResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': LoginResponse403
        }
    },
    tags=['system_account']
)
async def verify_email(
    email: EmailStr = Query(...), 
    key_verify: str = Query(...)
):
      
    try:
        user = SYSTEM['users'].find_one_and_update(
            {
                'email': {
                    '$eq': email
                },
                'key_verify': key_verify
            },
            {
                '$set': {
                    'is_verified': True
                }
            },
            return_document=ReturnDocument.AFTER
        )
        if user is None:
            msg = 'Link không tồn tại!'
            return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)
        else:
            user = SYSTEM[USER_COLLECTION].find_one_and_update(
                filter={
                    'email': {
                        '$eq': email
                    }
                },
                update={
                    '$unset': {
                        'key_verify': ''
                    }
                }
            )
            return JSONResponse(content={'status': 'success'}, status_code=status.HTTP_200_OK)
    except:
        msg = 'Link không tồn tại!'
        return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_404_NOT_FOUND)


