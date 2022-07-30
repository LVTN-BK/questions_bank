from fastapi import status, Form
from fastapi import Body, Depends
from app.utils.account import send_reset_password_email
from models.define.user import UserInfo
from models.request.account import DATA_Update_Account, DATA_Update_Email, DATA_Update_Password
from pymongo.collection import ReturnDocument
from starlette.responses import JSONResponse
from configs.settings import SYSTEM, USER_COLLECTION, USERS_PROFILE, app
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

# from cryptography.fernet import Fernet

from models.response.account import CreateAccountResponse200, CreateAccountResponse403, GetAccount200, GetAccount403, LoginResponse200, LoginResponse403, PutResetPasswordResponse200, PutResetPasswordResponse400, ResetPasswordResponse201, ResetPasswordResponse404, Token, User

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
    user = SYSTEM['users'].find_one(
        {
            'email': {
                '$eq': email
            },
            'is_verified': True
        }
    )
    if user is None:
        msg = 'Tài khoản không tồn tại hoặc chưa xác thực!'
        return JSONResponse(content={'status': 'Failed!', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)
    # Check verify email
    ###############################################

    try:
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

            user_info = SYSTEM[USERS_PROFILE].find_one({'user_id': str(user.get('_id'))})
            del user_info['_id']

            # user_info_return = UserInfo(id=str(user.get('_id')), avatar=user_info.get('avatar'))
            return JSONResponse(content={'token': user.get('token'), 'user': user_info},
                                status_code=status.HTTP_200_OK)
    except:
        pass
    msg = 'Tài khoản hoặc mật khẩu không đúng!'
    return JSONResponse(content={'status': 'Failed', 'msg': msg}, status_code=status.HTTP_400_BAD_REQUEST)

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
    # Check if user already exist
    if SYSTEM['users'].find({"email": {"$eq": email}}).count():
        return JSONResponse(content={
            "status": "Failed",
            "msg": "Email is existing for another account"
        }, status_code=status.HTTP_403_FORBIDDEN)
    

    # #Thêm encrypt password
    # key = Fernet.generate_key()
    # fernet = Fernet(key)

    user = User(
        name=name,
        # token=token,
        # secret_key=secret_key,
        email=email,
        hashed_password=get_password_hash(password),
        # encrypt_password=fernet.encrypt(password.encode()), #pass
        # encrypt_key=key,                                     #key
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
        'access_token': access_token
    }, status_code=status.HTTP_200_OK)

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
        return JSONResponse(content={'status': 'Failed!'}, status_code=status.HTTP_400_BAD_REQUEST)

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
        return JSONResponse(content={'status': 'Failed!'}, status_code=status.HTTP_400_BAD_REQUEST)

#===========================================
#=================UPDATE_EMAIL==============
#===========================================
@app.put(
    path='/update_email',
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
async def update_email(
    data1: DATA_Update_Email,
    data2: dict = Depends(valid_headers)
):
    logger().info('=====================update_email======================')
    user = SYSTEM['users'].find_one({'email': {'$eq': data2.get('email')}})
    data1 = jsonable_encoder(data1)
    if user is None:
        return JSONResponse(content={'status': 'Email not exist'}, status_code=status.HTTP_403_FORBIDDEN)
    try:
        if verify_password(data1.get('password'), user.get('hashed_password')):
            # Create new access token for user
            # secret_key = user.get('secret_key')
            access_token= create_access_token(
                data={
                    'email': data1.get('email'),
                    'user_id': str(user.get('_id'))
                }
            )

            # update in user table
            user = SYSTEM['users'].find_one_and_update(
                {'email': {'$eq': data2.get('email')}},
                {
                    '$set': {
                        'email': data1.get('email'),
                        'token.access_token': access_token,
                        # 'secret_key': secret_key
                    }
                },
                return_document=ReturnDocument.AFTER
            )

            # update in user information table
            query_update = {
                '$set': {
                    'email': data1.get('email')
                }
            }
            SYSTEM[USERS_PROFILE].find_one_and_update(
                {'user_id': str(user.get('_id'))},
                query_update
            )

            data = {
                'access_token': access_token, 
                # 'secret_key': secret_key,
                'email': data1.get('email')
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
    except Exception as Argument:
        logging.exception("Error occurred")
    msg = 'maybe password was wrong'
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
    email: EmailStr = Form(..., description='Email khôi phục mật khẩu'),
):
    """ 
        Khôi phục lại mật khẩu, hệ thống gửi mail kèm theo mã để khôi phục lại mật khẩu
    """
    import datetime
    import secrets
    keyonce = secrets.token_urlsafe(6)
    expire_in = datetime.datetime.now() + datetime.timedelta(minutes=30)
    expire_at_timestamp = expire_in.timestamp()

    user = SYSTEM[USER_COLLECTION].find_one(
        filter={'email': {'$eq': email}}
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Email chưa đăng ký tài khoản!'}, status_code=status.HTTP_404_NOT_FOUND)
    
    # Check if keyonce is not used
    await send_reset_password_email([email], keyonce=keyonce)
    SYSTEM[USER_COLLECTION].find_one_and_update(
        filter={'email': {'$eq': email}},
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
    keyonce: str = Form(..., description='Mã một lần để khôi phục mật khẩu'),
    password: str = Form(..., description='Mật khẩu lần một'),
    re_password: str = Form(..., description='Mật khẩu lần hai'),
):
    """Khôi phục lại mật khẩu"""
    if password != re_password:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mật khẩu không khớp!'}, status_code=status.HTTP_400_BAD_REQUEST)
    user = SYSTEM[USER_COLLECTION].find_one_and_update(
        filter={
            'keyonce': {'$eq': keyonce}, 'keyonce_expire_at': {'$gte': datetime.now().timestamp()}
        },
        update={
            '$set': {
                'tokens': [],
                'hashed_password': get_password_hash(password),
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
