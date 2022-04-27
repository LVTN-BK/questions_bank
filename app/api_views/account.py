from fastapi import status, Form
from fastapi import Body, Depends
from models.request.account import DATA_Update_Account
from pymongo.collection import ReturnDocument
from starlette.responses import JSONResponse
from configs.settings import SYSTEM, USER_COLLECTION, USERS_PROFILE, app
from app.secure._password import *
from app.secure._token import *
from app.utils._header import valid_headers
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
                    'user_id': str(user.get('_id'))
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
        name: str = Form(..., description='name'),
        password: str = Form(..., description='Password'),
):
    # Check if user already exist
    if SYSTEM['users'].find({"email": {"$eq": email}}).count():
        return JSONResponse(content={
            "status": "Failed",
            "msg": "Email is existing for another account"
        }, status_code=status.HTTP_403_FORBIDDEN)
    

    #Thêm encrypt password
    key = Fernet.generate_key()
    fernet = Fernet(key)

    user = User(
        name=name,
        # token=token,
        # secret_key=secret_key,
        email=email,
        hashed_password=get_password_hash(password),
        encrypt_password=fernet.encrypt(password.encode()), #pass
        encrypt_key=key,                                     #key
        datetime_created=datetime.now()
    )

    # Create user in db
    user_id = SYSTEM[USER_COLLECTION].insert_one(
        jsonable_encoder(user)
    ).inserted_id

    # insert to user profile
    query_profile = {
        'user_id': str(user_id),
        'name': name
    }
    SYSTEM[USERS_PROFILE].insert_one(
        query_profile
    )

    # Update access token, secret key
    access_token, secret_key = create_access_token(
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
            'token': jsonable_encoder(token),
            'secret_key': secret_key,
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


