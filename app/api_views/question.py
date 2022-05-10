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


#========================================================
#====================CREATE_QUESTION=====================
#========================================================
@app.post(
    path='/create_question',
    responses={
        status.HTTP_200_OK: {
            'model': LoginResponse200
        },
        status.HTTP_403_FORBIDDEN: {
            'model': LoginResponse403
        }
    },
    tags=['questions']
)
async def create_question(
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

            user_info = SYSTEM[USERS_PROFILE].find_one({'user_id': str(user.get('_id'))})
            del user_info['_id']

            # user_info_return = UserInfo(id=str(user.get('_id')), avatar=user_info.get('avatar'))
            return JSONResponse(content={'token': user.get('token'), 'secret_key': secret_key, 'user': user_info},
                                status_code=status.HTTP_200_OK)
    except:
        pass
    return JSONResponse(content={'status': 'Failed'}, status_code=status.HTTP_403_FORBIDDEN)
