from fastapi import status, Form
from fastapi import Body
from pymongo.collection import ReturnDocument
from starlette.responses import JSONResponse
from configs.settings import SYSTEM, app
from app.secure._password import *
from app.secure._token import *
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

from cryptography.fernet import Fernet

from models.response.account import CreateAccountResponse200, CreateAccountResponse403, GetAccount200, GetAccount403, LoginResponse200, LoginResponse403, Token, User

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
    user = SYSTEM['users'].find_one({'email': {'$eq': email}})
    if user is None:
        return JSONResponse(content={'status': 'Email not exist'}, status_code=status.HTTP_403_FORBIDDEN)
    try:
        if verify_password(password, user.get('hashed_password')):
            # Create new access token for user
            secret_key = user.get('secret_key')
            access_token, _ = create_access_token(
                data={
                    'email': user.get('email'),
                    'username': user.get('username')
                },
                secret_key=secret_key
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
            return JSONResponse(content={'token': user.get('token'), 'secret_key': secret_key},
                                status_code=status.HTTP_200_OK)
    except:
        pass
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)

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
        email: EmailStr = Form(..., description='Email'),
        username: str = Form(..., description='Username'),
        password: str = Form(..., description='Password'),
):
    # Check if user already exist
    if SYSTEM['users'].find({"email": {"$eq": email}}).count():
        return JSONResponse(content={
            "status": "Failed",
            "msg": "Email is existing for another account"
        }, status_code=status.HTTP_403_FORBIDDEN)
    # Create user in db
    access_token, secret_key = create_access_token(
        data={
            'email': email,
            'username': username
        }
    )

    token = Token(
        access_token=access_token,
        token_type='Bearer'
    )

    #Thêm encrypt password
    key = Fernet.generate_key()
    fernet = Fernet(key)

    user = User(
        username=username,
        token=token,
        secret_key=secret_key,
        email=email,
        hashed_password=get_password_hash(password),
        encrypt_password=fernet.encrypt(password.encode()), #pass
        encrypt_key=key,                                     #key
        datetime_created=datetime.now()
    )

    SYSTEM['users'].insert_one(
        jsonable_encoder(user)
    )

    user = SYSTEM['users'].find_one(
        {'email': {'$eq': email}},
    )

    # # add ma_tv
    # ma_tv = str(user.get('_id'))
    # SYSTEM['users'].update_one(
    #     {'email': {'$eq': email}},
    #     {
    #         '$set': {
    #             'ma_tv': ma_tv
    #         }
    #     }
    # )

    return JSONResponse(content={
        'status': 'Created',
        'access_token': access_token
    }, status_code=status.HTTP_200_OK)

#===========================================
#==============GET_ACCOUNT_INFO=============
#===========================================
@app.post(
    path= '/get_account_info',
    responses={
        status.HTTP_200_OK: {
            'model': GetAccount200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': GetAccount403
        }
    },
    tags=['system_account']
)
async def get_account_info(email: EmailStr = Form(...)):
    user = SYSTEM['users'].find_one({'email': {'$eq': email}})
    if user is None:
        return JSONResponse(content={'status': 'Email not exist'}, status_code=status.HTTP_403_FORBIDDEN)
    else:
        try:
            email = user.get('email')

            key = user.get('encrypt_key')
            fernet = Fernet(key)

            encrypt_password = bytes(user.get('encrypt_password'), 'utf-8')
            password=fernet.decrypt(encrypt_password).decode()

            return JSONResponse(content={'email': email, 'password': password}, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger().error(e)
            return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)