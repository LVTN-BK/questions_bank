import subprocess
import shlex
import jwt
from datetime import datetime, timedelta
from typing import Optional

cmd = "openssl rand -hex 32"
completed_process = subprocess.run(shlex.split(cmd), capture_output=True)
stdout = completed_process.stdout.decode(encoding='utf-8').strip('\n')

SECRET_KEY = stdout
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, secret_key=None):
    """Return JWT and it's secret key for decoding
    Args:
        data (dict): data to be encoded
        expires_delta (timedelta): Specify if there's limited time for token life
        secret_key (str): secret_key for encoding/decoding JWT token
    Returns:
        tuple: contains encoded_jwt, SECRET_KEY
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if not secret_key:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt, secret_key


def is_not_expired(encode_jwt, SECRET_KEY):
    """Check if token is expired or not
    Args:
        encode_jwt (str): JWT token for checking
        SECRET_KEY (str): Key for decoding JWT token
    Returns:
        bool: True if not expired, False otherwise
    """
    try:
        jwt.decode(encode_jwt, SECRET_KEY, algorithms=ALGORITHM)
    except Exception:
        return False
    return True


def get_data_from_access_token(encode_jwt, SECRET_KEY):
    """Check if token is expired or not
        Args:
            encode_jwt (str): JWT token for checking
            SECRET_KEY (str): Key for decoding JWT token
        Returns:
            dict: data from access token
    """
    return jwt.decode(encode_jwt, SECRET_KEY, algorithms=ALGORITHM)