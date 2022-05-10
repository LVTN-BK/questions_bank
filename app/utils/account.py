import os
from configs.logger import logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


async def send_reset_password_email(to_emails, data: dict):
    """Gửi email reset mật khẩu tài khoản
    Args:
        to_email (list, tuple, str): Email nhận hoặc danh sách email nhận

    Returns:
        True if sent successfully else False
    """
    message = Mail(
        from_email=os.environ.get('SENDGRID_MAIL'),
        to_emails=to_emails)
    message.dynamic_template_data = data
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        logger().error(e.message)
        return False
    return True