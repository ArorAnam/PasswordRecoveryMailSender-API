from fastapi import FastAPI, BackgroundTasks, Request, Form
from starlette.responses import JSONResponse, RedirectResponse
from fastapi_mail.fastmail import FastMail
from fastapi import Header, File, Body, Query, UploadFile
from pydantic import BaseModel, EmailStr
from fastapi.templating import Jinja2Templates
from typing import Optional

import random
import string

# Initialize the fastpai APP
app = FastAPI()

# html template for html email response
html = """
<html> 
<body>
<p>Hi This test mail
<br>Thanks for using Fastapi-mail</p> 
</body> 
</html>
"""

# Pydantic mdodel for email, passcode pair
class EmailSchema(BaseModel):
    email: str
    passcode: str


# Intilize templates variable by defining the containing directory
templates = Jinja2Templates(directory="templates")


def get_random_alphanumeric_string(length):
    """Generates a random alphanumeric string of given length

    Parameters
    ----------
    length : int
        The length of random string to be generated

    Returns
    -------
    result_str : string
        A random string
    """
    letters_and_digits = string.ascii_letters + string.digits
    result_str = "".join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def send_email(background_tasks: BackgroundTasks, request: Request):
    """Sends an email with a defines template containing the passcode
       Email is intialized at '/' endpoint as global
       You have to fill in here your email and password from which you want to send the maail (GMAIL)

    Parameters
    ----------
    background_tasks : BackgroudTasks
        For sending the mail in the background
    request : Request
        For using JinJaTemplates as a response

    Returns
    -------
    template : Jinaja Template
        "after_email_sent_response.html"
    """

    template = """
        <html> 
        <body>
        <p>Hi !!!
        <br>Thanks for using Fastapi-mail</p>
        <p> Your passcode is : %s </p> 
        </body> 
        </html>
        """ % (
        code
    )

    mail = FastMail(
        email="your-email-here",
        password="your-password-here",
        tls=True,
        port="587",
        service="gmail",
    )

    background_tasks.add_task(
        mail.send_message,
        recipient=Email,
        subject="testing HTML",
        body=template,
        text_format="html",
    )

    return templates.TemplateResponse(
        "after_email_sent_response.html", {"request": request}
    )


@app.get("/")
async def get_email(request: Request):
    """Returns the homepage template where you enter your email"""

    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/send_mail")
async def send_mail(
    background_tasks: BackgroundTasks,
    request: Request,
    email: Optional[str] = Form(...),
):
    """End-point to send the mail. Generate the code and then calls the send_email function

    Parameters
    ----------
    background_tasks : BackgroudTasks
        For sending the mail in the background
    request : Request
        For using JinJaTemplates as a response
    email : string(Form)
        email which is sent as form reply from the '/' end-point

    Returns
    -------
    template : Jinaja Template
        Using the send_email funtion
    """

    if email:
        global code, Email
        Email = email
        code = get_random_alphanumeric_string(10)

    return send_email(background_tasks, request)


@app.get("/send_mail_again")
def send_mail_again(background_tasks: BackgroundTasks, request: Request):
    """Resends the mail when user clicks in the resend email button"""

    return send_email(background_tasks, request)


@app.post("/account_recovery/")
async def verify_passcode(request: Request, passcode: Optional[str] = Form(...)):
    """Checks if the passcode entered by the user is correct or not

    Parameters
    ----------
    request : Request
        For using JinJaTemplates as a response
    passcode : string(Form)
        passcode which is sent as form reply

    Returns
    -------
    template : Jinaja Template
        "failed_verification.html"
    """

    result = ""
    if passcode == code:
        result = "successful"

        # give the result of passcode validation
        return templates.TemplateResponse(
            "successful_verification_result.html",
            {"request": request, "result": result},
        )
    else:
        result = "failed"

        return templates.TemplateResponse(
            "failed_verification.html", {"request": request, "result": result}
        )


@app.get("/re_enter_passcode")
async def re_enter_passcode(request: Request):
    """Returns "after_email_sent_response.html for re-entering of the passcode"""

    return templates.TemplateResponse(
        "after_email_sent_response.html", {"request": request}
    )
