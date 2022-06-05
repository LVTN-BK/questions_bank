from __future__ import print_function
import json
from configs.logger import logger
# import time
# import sib_api_v3_sdk
# from sib_api_v3_sdk.rest import ApiException
# from pprint import pprint
from starlette.responses import JSONResponse
from configs.settings import app
    
# from __future__ import print_function

import base64
from email.mime.text import MIMEText

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi.encoders import jsonable_encoder

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def gmail_send_message():
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # creds = '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'if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json')
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    # creds, _ = google.auth.default()

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText('This is automated draft mail 3')
        message['To'] = 'do.pro.st.vn17@gmail.com'
        message['From'] = 'hotro.qb@gmail.com'
        message['Subject'] = 'Automated draft'
        # encoded message
        # logger().info(jsonable_encoder(message))
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


# if __name__ == '__main__':
#     gmail_send_message()

@app.post("/email")
async def simple_send(
    # email: EmailSchema
    ) -> JSONResponse:
    gmail_send_message()

    # configuration = sib_api_v3_sdk.Configuration()
    # configuration.api_key['api-key'] = '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'

    # api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    # subject = "My Subject"
    # html_content = "<html><body><h1>This is my first transactional email </h1></body></html>"
    # sender = {"name":"Do Pham","email":"hotro.qb@gmail.com"}
    # to = [{"email":"do.pro.st.vn17@gmail.com","name":"Jane Doe"}]
    # # cc = [{"email":"example2@example2.com","name":"Janice Doe"}]
    # # bcc = [{"name":"John Doe","email":"example@example.com"}]
    # # reply_to = {"email":"replyto@domain.com","name":"John Doe"}
    # headers = {"Some-Custom-Name":"unique-id-1234"}
    # params = {"parameter":"My param value","subject":"New Subject"}
    # send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers, html_content=html_content, sender=sender, subject=subject)

    # try:
    #     api_response = api_instance.send_transac_email(send_smtp_email)
    #     pprint(api_response)
    # except ApiException as e:
    #     print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

