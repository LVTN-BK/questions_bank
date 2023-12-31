from configs.logger import logger
from fastapi import status, HTTPException, Header, Security
from app.secure._token import is_not_expired, get_data_from_access_token
from configs.settings import SYSTEM, USER_COLLECTION
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder

security = HTTPBearer()
async def valid_headers(
        Authorization: HTTPAuthorizationCredentials = Security(security)
        # s_key: str = Header(..., description='secret_key return by login'),
):
    """Check if access token valid for accessing api
    Args:
        Bearer (str): Bearer token
        s_key (str): Secret key
    Returns:
        bool: True if valid, otherwise False
    Raises:
        HTTPException: if token is not valid
    """
    logger().info('===========valid header===========')
    # logger().info(jsonable_encoder(Authorization))
    # authen = jsonable_encoder(Authorization)
    token = Authorization.credentials
    bearer = Authorization.scheme
    # logger().info(token)
    # logger().info(type(token))
    # bearer, token = Authorization.split(' ')
    if is_not_expired(encode_jwt=token):
        data = get_data_from_access_token(encode_jwt=token)
        email = data.get('email')
        user = SYSTEM[USER_COLLECTION].find_one(
            {
                'email': {'$eq': email},
                'is_disable': False
            }
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Access deny! User is banned!')
        token_type = user.get('token').get('token_type')
        if token_type != bearer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token type is not valid')
        if user and user.get('token').get('access_token') != token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token is not valid')
        return data
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token is not valid')