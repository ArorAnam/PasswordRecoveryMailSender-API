from fastapi import FastAPI, BackgroundTasks, Request, Form
from starlette.responses import JSONResponse
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


@app.get("/")
async def get_email(request: Request):

    return templates.TemplateResponse("index.html",
                        {
                            "request": request
                        })


@app.post("/send_mail")
async def send_mail(background_tasks: BackgroundTasks, request: Request, email: str = Form(...)):
    # this mail sending using fastapi background tasks, faster than the above one
    # Using Postman you can send post request, adding email in the body

    global code
    code = get_random_alphanumeric_string(10)

    template = """
        <html> 
        <body>
        <p>Hi This test mail using BackgroundTasks
        <br>Thanks for using Fastapi-mail</p>
        <p> Your passcode is : %s </p> 
        </body> 
        </html>
        """ % (code)


    # mail = FastMail(email="you-email-here", password="your-password", tls=True, port="587", service="gmail")
    mail = FastMail(email="arora.nam21@gmail.com", password="kjol#1897", tls=True, port="587", service="gmail")

    background_tasks.add_task(mail.send_message, recipient=email, subject="testing HTML", body=template,
                                text_format="html")

    return templates.TemplateResponse("after_email_sent_response.html",
                        {
                            "request": request
                        })


@app.post("/account_recovery/")
async def verify_passcode(request: Request, passcode: Optional[str] = Form(...)):

    result = ''
    if passcode == code:
        result = 'successful'
    else:
        result = 'failed'

    return templates.TemplateResponse("verification_result.html",
                            {
                                "request": request,
                                "result": result
                            })