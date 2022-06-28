#  Copyright (c) 2021.
import cloudinary.uploader
from configs.logger import logger



async def upload_image(user_id, attachment_image):
    attachment_image_url, attachment_image_public_id = '', ''
    try:
        file = getattr(attachment_image, 'file')
        if file:
            result = cloudinary.uploader.upload(file=file, folder=f'user/images/{user_id}')
            attachment_image_url = result.get('secure_url')
            attachment_image_public_id = result.get('public_id')
    except AttributeError:
        logger().info('================upload failed!===================')
        pass
    return attachment_image_url, attachment_image_public_id

async def upload_images(user_id, attachment_image):
    attachment_image_url, attachment_image_public_ids = [], []
    try:
        for image in attachment_image:
            # Loop over file attachment and upload to cloudinary
            file = getattr(image, 'file')
            if file:
                result = cloudinary.uploader.upload(file=file, folder=f'user/images/{user_id}')
                attachment_image_url.append(result.get('secure_url'))
                attachment_image_public_ids.append(result.get('public_id'))
    except AttributeError:
        pass
    return attachment_image_url, attachment_image_public_ids
