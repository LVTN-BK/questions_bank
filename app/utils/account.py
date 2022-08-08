from __future__ import print_function
from configs.logger import logger
# import time
from configs.settings import MAIL_API_KEY
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
# from pprint import pprint

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = MAIL_API_KEY



# async def send_reset_password_email(to_emails, keyonce: str):
#     """Create and send an email message
#     Print the returned  message id
#     Returns: Message object, including message id

#     Load pre-authorized user credentials from the environment.
#     TODO(developer) - See https://developers.google.com/identity
#     for guides on implementing OAuth2 for the application.
#     """
#     # creds = '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'if os.path.exists('token.json'):
#     creds = Credentials.from_authorized_user_file('token.json')
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json')
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     # creds, _ = google.auth.default()

#     try:
#         service = build('gmail', 'v1', credentials=creds)
#         msg = 'Vui lòng xác nhận địa chỉ email của bạn bằng cách nhập mã xác minh bên dưới. Mã có giá trị trong 30 phút'
#         html = f"""
#         <html>
#         <head></head>
#         <body>
#         <div style="text-align:center">
#             <p>{msg}</p>
#         </div><br>
#         <div style="text-align:center">
#             <h1><b>{keyonce}</b></h1><br>
#         </div>
#         </body>
#         </html>
#         """
#         message = MIMEText(html, 'html')
#         message['To'] = (', ').join(to_emails)
#         message['From'] = 'hotro.qb@gmail.com'
#         message['Subject'] = 'Reset Password - Question Banks'

#         encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#         create_message = {
#             'raw': encoded_message
#         }
#         send_message = (service.users().messages().send(userId="me", body=create_message).execute())
#     except HttpError as error:
#         logger().error(F'An error occurred: {error}')
#         return False
#     return True



async def send_reset_password_email(to_email: str, keyonce: str):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "Reset Password - Question Banks"
    msg = 'Vui lòng xác nhận địa chỉ email của bạn bằng cách nhập mã xác minh bên dưới. Mã có giá trị trong 30 phút'
    html_content = f"""
        <html>
        <head></head>
        <body>
        <div style="text-align:center">
            <p>{msg}</p>
        </div><br>
        <div style="text-align:center">
            <h1><b>{keyonce}</b></h1><br>
        </div>
        </body>
        </html>
        """
    sender = {"name":"Questions Bank","email":"hotro.qb@gmail.com"}
    to = [{"email":to_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        # pprint(api_response)
    except ApiException as e:
        logger().error("Exception when calling SMTPApi->send_transac_email: %s\n" % e)


# async def send_verify_email(to_emails: str, keyonce: str):
#     """Create and send an email message
#     Print the returned  message id
#     Returns: Message object, including message id

#     Load pre-authorized user credentials from the environment.
#     TODO(developer) - See https://developers.google.com/identity
#     for guides on implementing OAuth2 for the application.
#     """
#     # creds = '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'if os.path.exists('token.json'):
#     creds = Credentials.from_authorized_user_file('token.json')
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json')
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     # creds, _ = google.auth.default()

#     try:
#         service = build('gmail', 'v1', credentials=creds)
#         url = f'https://question-bank-be.herokuapp.com/verify_email?email={to_emails}&key_verify={keyonce}'
#         msg = 'Vui lòng xác nhận địa chỉ email của bạn bằng cách nhấp vào đường link bên dưới.'
#         html = f"""
#         <html>
#         <head></head>
#         <body>
#         <div style="text-align:center">
#             <p>{msg}</p>
#         </div><br>
#         <div style="text-align:center">
#             <h1><b>{url}</b></h1><br>
#         </div>
#         </body>
#         </html>
#         """
#         message = MIMEText(html, 'html')
#         message['To'] = to_emails
#         message['From'] = 'hotro.qb@gmail.com'
#         message['Subject'] = 'Reset Password - Question Banks'

#         encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#         create_message = {
#             'raw': encoded_message
#         }
#         send_message = (service.users().messages().send(userId="me", body=create_message).execute())
#     except HttpError as error:
#         logger().error(F'An error occurred: {error}')
#         return False
#     return True


async def send_verify_email(to_email: str, keyonce: str):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "Verify Your Email"
    url = f'https://question-bank-be.herokuapp.com/verify_email?email={to_email}&key_verify={keyonce}'
    msg = 'Vui lòng xác nhận địa chỉ email của bạn bằng cách nhấp vào đường link bên dưới.'
    html_content = f"""
        <html>
        <head></head>
        <body>
        <div style="text-align:center">
            <p>{msg}</p>
        </div><br>
        <div style="text-align:center">
            <h1><b>{url}</b></h1><br>
        </div>
        </body>
        </html>
        """
    sender = {"name":"Questions Bank","email":"hotro.qb@gmail.com"}
    to = [{"email":to_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        # pprint(api_response)
    except ApiException as e:
        logger().error("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
