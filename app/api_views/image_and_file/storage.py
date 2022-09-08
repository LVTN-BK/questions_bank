from datetime import datetime
from fastapi import BackgroundTasks, File, UploadFile, status, Depends
from starlette.responses import JSONResponse
from app.utils._header import valid_headers
from app.utils.upload_images import upload_image
from configs.settings import app
from configs.logger import *


#================================================
#=================UPLOAD_IMAGE===================
#================================================
@app.post(
    path="/upload_image",
    responses={
        status.HTTP_200_OK: {
            'model': '',
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': '',
        }
    },
    tags=['Storage'],
    # summary="Tạo task gửi yêu cầu tham gia group",
    description="Tải hình lên và trả về url"
)
async def store_image(
    image: UploadFile= File(...,description="file as UploadFile"),
    valid_headers: dict = Depends(valid_headers)
):
    logger().info('==========api upload image============')

    try:
        user_id = valid_headers.get('user_id')
        #upload avatar to cloud
        image_url, image_public_id = await upload_image(user_id, image)

        return JSONResponse(content={'url': image_url}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger().error(e)
        return JSONResponse(content={'status': 'failed'}, status_code=status.HTTP_400_BAD_REQUEST)