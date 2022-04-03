from datetime import datetime
from fastapi import status, Depends
from starlette.responses import JSONResponse

from app.utils._headers import valid_headers
from configs.settings import app
from models.request import all_data_model
from configs.logger import *
from app.secure._token import *
from models.response.all_response import CreateTaskFail400, CreateTaskOK201, GetTaskResultFail400, GetTaskResultOK201


#===========================================
#==============JOIN_GROUP===================
#===========================================
@app.post(
    path="/join_group",
    responses={
        status.HTTP_201_CREATED: {
            'model': CreateTaskOK201,
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': CreateTaskFail400,
        }
    },
    tags=['Group'],
    # summary="Tạo task gửi yêu cầu tham gia group",
    description="Tạo task gửi yêu cầu tham gia nhóm và lưu thông tin task lên datalake"
)
async def join_group(
    data: all_data_model.DATA_Auto_comment,
    valid_headers: dict = Depends(valid_headers)
):
    logger.info('==========api create task join_group============')

    return JSONResponse(content={'status': 'Done'}, status_code=status.HTTP_201_CREATED)