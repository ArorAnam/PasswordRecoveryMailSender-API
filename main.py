from fastapi import FastAPI, BackgroundTasks, Request, Form
from starlette.responses import JSONResponse, RedirectResponse
from fastapi_mail.fastmail import FastMail
from fastapi import Header, File, Body, Query, UploadFile
from pydantic import BaseModel, EmailStr
from fastapi.templating import Jinja2Templates
from typing import Optional

import random
import string

app = FastAPI()

html = """
<html> 
<body>
<p>Hi This test mail
<br>Thanks for using Fastapi-mail</p> 
</body> 
</html>
"""


class EmailSchema(BaseModel):
    email: str

class Passcode(BaseModel):
    password: str


templates = Jinja2Templates(directory="templates")


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def send_email(background_tasks: BackgroundTasks, request: Request):
    
    template = """
        <html> 
        <body>
        <p>Hi !!!
        <br>Thanks for using Fastapi-mail</p>
        <p> Your passcode is : %s </p> 
        </body> 
        </html>
        """ % (code)

    mail = FastMail(email="your-email-here", password="your-password-here", tls=True, port="587", service="gmail")

    background_tasks.add_task(mail.send_message, recipient=Email, subject="testing HTML", body=template,
                                text_format="html")

    return templates.TemplateResponse("after_email_sent_response.html",
                        {
                            "request": request
                        })


@app.get("/")
async def get_email(request: Request):

    return templates.TemplateResponse("index.html",
                        {
                            "request": request
                        })


@app.post("/send_mail")
async def send_mail(background_tasks: BackgroundTasks, request: Request, email: Optional[str] = Form(...)):
    # this mail sending using fastapi background tasks, faster than the above one
    # Using Postman you can send post request, adding email in the body

    if email:
        global code, Email
        Email = email
        code = get_random_alphanumeric_string(10)

    return send_email(background_tasks, request)


@app.get("/send_mail_again")
def send_mail_again(background_tasks: BackgroundTasks, request: Request):
    return send_email(background_tasks, request)


@app.post("/account_recovery/")
async def verify_passcode(request: Request, passcode: Optional[str] = Form(...)):

    result = ''
    if passcode == code:
        result = 'successful'

        # give the result of passcode validation
        return templates.TemplateResponse("successful_verification_result.html",
                                {
                                    "request": request,
                                    "result": result
                                })
    else:
        result = 'failed'

        return templates.TemplateResponse("failed_verification.html",
                                {
                                    "request": request,
                                    "result": result
                                })

    # response = RedirectResponse(url='/')


@app.get("/re_enter_passcode")
async def re_enter_passcode(request: Request):

    return templates.TemplateResponse("after_email_sent_response.html",
                        {
                            "request": request
                        })